# Исправление проблем сборки Frontend контейнера

## Проблемы

При сборке frontend контейнера возникали последовательно три ошибки:

### Ошибка 1: Cannot find module 'styled-jsx/package.json'
```
Error: Cannot find module 'styled-jsx/package.json'
```

### Ошибка 2: The module 'react' was not found
```
Error: The module 'react' was not found. 
Next.js requires that you include it in 'dependencies' of your 'package.json'
```

### Ошибка 3: ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY
```
ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY
Aborted removal of modules directory due to no TTY
```

## Корневая причина

**Next.js + pnpm + Docker = тройная проблема**

1. **Проблема hoisting:** pnpm по умолчанию не поднимает (hoist) вложенные зависимости на верхний уровень `node_modules`, в отличие от npm/yarn
2. **Next.js требования:** Next.js ожидает что `styled-jsx`, `react` и другие встроенные модули доступны на верхнем уровне
3. **Конфликт путей:** Двойное копирование `package.json` в Dockerfile создавало конфликт структуры директорий
4. **TTY проблема:** pnpm пытался запросить подтверждение на удаление node_modules в неинтерактивной среде Docker

## Решение

### 1. ✅ Создан `frontend/.npmrc`

Файл конфигурации pnpm для правильной работы с Next.js:

```ini
shamefully-hoist=true
public-hoist-pattern[]=*styled-jsx*
```

**Что делает:**
- `shamefully-hoist=true` - включает полный hoisting всех зависимостей (режим совместимости с npm)
- `public-hoist-pattern[]=*styled-jsx*` - явно поднимает styled-jsx и его зависимости

### 2. ✅ Упрощен `devops/Dockerfile.frontend`

**Было (проблемный вариант):**
```dockerfile
# Копировали файлы по частям
COPY frontend/.npmrc ./
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/. ./  # <- Двойное копирование создавало конфликт!
```

**Стало (правильный вариант):**
```dockerfile
FROM node:20-slim

WORKDIR /app

# Установить pnpm
RUN npm install -g pnpm@10.18.3

# Скопировать ВСЕ файлы frontend сразу (node_modules исключен через .dockerignore)
COPY frontend/ ./

# Убедиться что node_modules не существует
RUN rm -rf node_modules

# Установить зависимости с флагами для совместимости
RUN pnpm install --frozen-lockfile --shamefully-hoist --force

# Собрать production build
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
```

**Ключевые изменения:**
- ✅ Копируем все файлы `frontend/` одним `COPY` (включая `.npmrc`, `package.json`, весь код)
- ✅ Явно удаляем `node_modules` командой `rm -rf` перед установкой
- ✅ Используем флаг `--shamefully-hoist` для полного hoisting (совместимость с Next.js)
- ✅ Используем флаг `--force` для неинтерактивной пересборки node_modules
- ✅ Нет двойного копирования файлов
- ✅ `node_modules` автоматически исключается через `.dockerignore`

## Почему это работает

1. **Единое копирование:** Все файлы копируются сразу, сохраняя правильную структуру
2. **Явная очистка:** `rm -rf node_modules` гарантирует чистое состояние перед установкой
3. **Правильный hoisting:** Флаг `--shamefully-hoist` заставляет pnpm работать как npm
4. **Неинтерактивный режим:** Флаг `--force` позволяет pnpm работать без запросов подтверждения (no TTY)
5. **Конфигурация .npmrc:** Дополнительно настраивает hoisting для styled-jsx
6. **Исключение node_modules:** `.dockerignore` гарантирует что локальные node_modules не попадут в образ

## Проверка решения

### Шаг 1: Очистить старые образы

```bash
# Удалить старый образ frontend
docker rmi systech-aidd-frontend

# Или полная очистка
docker system prune -a
```

### Шаг 2: Пересобрать frontend

```bash
# Только frontend
docker-compose build frontend

# Или все сервисы
make docker-build
```

### Шаг 3: Запустить и проверить логи

```bash
# Запустить
make docker-up

# Проверить логи
make docker-logs-frontend
```

**Ожидаемый вывод (успех):**
```
systech-aidd-frontend | > frontend@0.1.0 start
systech-aidd-frontend | > next start
systech-aidd-frontend | 
systech-aidd-frontend |   ▲ Next.js 15.5.6
systech-aidd-frontend |   - Local:        http://localhost:3000
systech-aidd-frontend | 
systech-aidd-frontend | ✓ Ready in XXXms
```

### Шаг 4: Открыть в браузере

```bash
# Откройте
http://localhost:3000
```

Должна открыться страница без ошибок.

## Альтернативное решение (если проблема сохраняется)

### Вариант 1: Использовать npm вместо pnpm

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --production

COPY frontend/ ./
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Вариант 2: Явно установить проблемные модули

В `frontend/package.json` добавить:
```json
{
  "dependencies": {
    "styled-jsx": "5.1.1"
  }
}
```

### Вариант 3: node-linker hoisted

В `frontend/.npmrc`:
```ini
node-linker=hoisted
```

## Файлы изменены

1. ✅ `frontend/.npmrc` - создан
2. ✅ `devops/Dockerfile.frontend` - упрощен
3. ✅ `devops/TROUBLESHOOTING.md` - обновлена документация
4. ✅ `devops/FRONTEND_BUILD_FIX.md` - этот файл

## Дополнительная информация

### Почему pnpm имеет эти проблемы?

pnpm использует symlinks и строгую изоляцию зависимостей. Это отлично для:
- ✅ Экономии дискового пространства
- ✅ Предотвращения "phantom dependencies"
- ✅ Более быстрой установки

Но может создавать проблемы с:
- ❌ Legacy инструментами, ожидающими flat node_modules
- ❌ Next.js встроенными зависимостями
- ❌ Некоторыми bundlers

### Флаг --shamefully-hoist

Флаг называется "shamefully" (стыдливо), потому что он отключает главное преимущество pnpm - строгую изоляцию зависимостей. Но для совместимости с Next.js это необходимо в Docker образе.

### Почему в локальной разработке работает?

В локальной разработке у вас может быть:
- Другая версия pnpm
- Глобальные настройки pnpm
- Кеш зависимостей
- Другая структура node_modules

Docker всегда собирает "с нуля", поэтому проблемы проявляются явно.

## Заключение

**Проблема решена!** ✅

Frontend контейнер теперь должен собираться без ошибок. Если проблемы сохраняются, см. альтернативные решения выше или обратитесь к `devops/TROUBLESHOOTING.md`.

---

**Команда для повторной сборки:**
```bash
make docker-build && make docker-up && make docker-logs-frontend
```

