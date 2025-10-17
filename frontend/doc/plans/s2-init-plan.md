<!-- 50447a1f-83b5-4b36-be64-5adda3b8eca2 886b52ad-5024-4a35-9d52-48c2fe6986fd -->
# Sprint F-S2: Инициализация Frontend проекта

## Обзор

Создание базовой структуры frontend проекта с использованием Next.js (Pages Router), TypeScript, shadcn/ui, Tailwind CSS и pnpm. Определение концепции UI, настройка инструментов разработки и создание команд для работы с проектом.

## Технологический стек

- **Framework:** Next.js (Pages Router)
- **Язык:** TypeScript
- **UI Library:** shadcn/ui
- **Styling:** Tailwind CSS
- **Пакетный менеджер:** pnpm

## Задачи

### 1. Создать документ концепции frontend

**Файл:** `frontend/doc/front-vision.md`

По аналогии с `docs/vision.md` создать документ, описывающий:

- Технологический стек frontend
- Принципы разработки UI (компонентный подход, TypeScript-first)
- Структуру frontend проекта
- Соглашения по именованию файлов и компонентов
- Подход к стилизации (Tailwind CSS + shadcn/ui)
- Управление состоянием (если планируется)
- Требования к тестированию frontend (будущее)

### 2. Инициализировать Next.js проект

**Директория:** `frontend/`

Выполнить инициализацию проекта:

```bash
cd frontend
pnpm create next-app@latest . --typescript --tailwind --no-app --no-src-dir --import-alias "@/*"
```

Параметры:

- `--typescript` - TypeScript
- `--tailwind` - Tailwind CSS
- `--no-app` - Pages Router (не App Router)
- `--no-src-dir` - без директории src (файлы в корне)
- `--import-alias "@/*"` - алиас для импортов
- ESLint - Yes (при запросе)

### 3. Настроить shadcn/ui

Инициализировать shadcn/ui в проекте:

```bash
cd frontend
pnpm dlx shadcn@latest init
```

Выбрать параметры:

- Style: Default
- Base color: Slate (или другой нейтральный)
- CSS variables: Yes

### 4. Создать базовую структуру проекта

Организовать структуру директорий:

```
frontend/
├── pages/              # Next.js Pages Router
│   ├── _app.tsx        # Общая обертка приложения
│   ├── _document.tsx   # HTML документ
│   └── index.tsx       # Главная страница
├── components/         # React компоненты
│   └── ui/            # shadcn/ui компоненты (создается автоматически)
├── lib/               # Утилиты и helpers (создается shadcn)
├── types/             # TypeScript типы и интерфейсы
│   ├── api.ts         # Типы для работы с API
│   └── index.ts       # Экспорт всех типов
├── styles/            # Глобальные стили
│   └── globals.css    # Tailwind directives
├── public/            # Статические файлы
├── doc/               # Документация (существующая)
│   └── adr/          # Architecture Decision Records
├── reference/         # Референсы (существующие)
├── .env.local.example # Пример переменных окружения
├── .env.local         # Переменные окружения (в .gitignore)
├── README.md          # Инструкции по установке и запуску
├── package.json       # Зависимости npm
├── tsconfig.json      # TypeScript конфигурация
├── tailwind.config.ts # Tailwind конфигурация
├── next.config.js     # Next.js конфигурация
└── .eslintrc.json     # ESLint конфигурация
```

### 5. Создать базовую страницу-заглушку

**Файл:** `frontend/pages/index.tsx`

Создать простую главную страницу с:

- Заголовком проекта "Systech AIDD Dashboard"
- Кратким описанием
- Информацией о текущем статусе ("In Development")
- Использование компонента Button из shadcn/ui для демонстрации

### 6. Настроить TypeScript

Обновить `tsconfig.json`:

- Strict mode enabled
- Path aliases настроены (`@/*`)
- Исключить `node_modules`, `.next`

### 7. Настроить Next.js конфигурацию

**Файл:** `frontend/next.config.js`

Базовая конфигурация:

- React Strict Mode enabled
- Настройка для работы с API (если нужно)

### 8. Создать команды в корневом Makefile

Добавить команды для работы с frontend:

```makefile
# Frontend commands
frontend-install:
	cd frontend && pnpm install

frontend-dev:
	cd frontend && pnpm dev

frontend-build:
	cd frontend && pnpm build

frontend-lint:
	cd frontend && pnpm lint

frontend-typecheck:
	cd frontend && pnpm tsc --noEmit
```

### 9. Добавить базовые компоненты shadcn/ui

Установить несколько базовых компонентов для демонстрации:

```bash
cd frontend
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add card
```

### 10. Создать .gitignore для frontend

**Файл:** `frontend/.gitignore`

Добавить игнорируемые файлы:

- `node_modules/`
- `.next/`
- `out/`
- `*.log`
- `.env*.local`

### 11. Создать директорию для типов

**Директория:** `frontend/types/`

Создать структуру для хранения TypeScript типов и интерфейсов:

- `api.ts` - типы для работы с API (на будущее)
- `index.ts` - экспорт всех типов

### 12. Настроить переменные окружения

**Файлы:** `frontend/.env.local.example`, `frontend/.env.local`

Создать файлы для переменных окружения:

- `.env.local.example` - пример с описанием переменных (коммитится в git)
- `.env.local` - реальные значения (в .gitignore)

Добавить переменные:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 13. Создать ADR для технологического стека

**Файл:** `frontend/doc/adr/0001-frontend-tech-stack.md`

По аналогии с `docs/adr/0001-postgresql-raw-sql-alembic.md` создать документ с обоснованием выбора:

- Next.js (Pages Router vs App Router)
- TypeScript
- shadcn/ui (почему не Material-UI, Ant Design и т.д.)
- Tailwind CSS
- pnpm (vs npm, yarn)

### 14. Создать README.md для frontend

**Файл:** `frontend/README.md`

Инструкции по установке и запуску:

- Требования (Node.js, pnpm)
- Установка зависимостей
- Запуск dev сервера
- Сборка production
- Линтинг и проверка типов
- Структура проекта
- Работа с shadcn/ui компонентами

### 15. Создать план спринта

**Файл:** `frontend/doc/plans/f2-frontend-init-plan.md`

Сохранить копию текущего плана для истории.

### 16. Проверить работу команд

Проверить что все команды работают корректно:

- `pnpm dev` - запуск dev сервера
- `pnpm build` - сборка production
- `pnpm lint` - проверка ESLint
- `pnpm tsc --noEmit` - проверка типов TypeScript

### 17. Обновить roadmap

**Файл:** `docs/frontend-roadmap.md`

- Изменить статус F-S2 с "📋 Planned" на "✅ Completed"
- Добавить дату завершения (17 октября 2025)
- Добавить ссылку на план реализации `frontend/doc/plans/f2-frontend-init-plan.md` в таблицу спринтов

## Результат

После выполнения спринта:

- ✅ Инициализирован Next.js проект с TypeScript
- ✅ Настроен Tailwind CSS
- ✅ Интегрирован shadcn/ui с базовыми компонентами
- ✅ Создана базовая структура проекта
- ✅ Настроены инструменты разработки (ESLint, TypeScript)
- ✅ Созданы команды для запуска и проверки качества
- ✅ Документирована концепция frontend
- ✅ Создана базовая страница-заглушка

Frontend проект готов к разработке дашборда в следующем спринте (F-S3).

### To-dos

- [ ] Создать frontend/doc/front-vision.md с концепцией UI и принципами разработки
- [ ] Инициализировать Next.js проект с TypeScript, Tailwind CSS и Pages Router
- [ ] Настроить shadcn/ui и установить базовые компоненты (button, card)
- [ ] Создать базовую структуру проекта (pages, components, lib, styles)
- [ ] Создать главную страницу-заглушку с использованием shadcn/ui компонентов
- [ ] Добавить frontend команды в корневой Makefile (install, dev, build, lint, typecheck)
- [ ] Создать frontend/.gitignore для Next.js проекта
- [ ] Создать план спринта (f2-frontend-init-plan.md) и обновить roadmap

