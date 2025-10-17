# Systech AIDD Frontend

Frontend приложение для дашборда статистики по диалогам и веб-чата AI-Driven Dialogue System.

## Технологический стек

- **Framework:** Next.js 15+ (Pages Router)
- **Язык:** TypeScript 5+ (strict mode)
- **UI Library:** shadcn/ui (Radix UI + Tailwind CSS)
- **Styling:** Tailwind CSS 4+
- **Пакетный менеджер:** pnpm

## Требования

- **Node.js:** 18.17 или выше
- **pnpm:** 8.0 или выше

### Установка pnpm

```bash
npm install -g pnpm
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pnpm install
```

### 2. Настройка переменных окружения

Создайте файл `.env.local` на основе `.env.local.example`:

```bash
cp .env.local.example .env.local
```

Отредактируйте `.env.local` и укажите URL backend API:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Запуск dev сервера

```bash
pnpm dev
```

Откройте [http://localhost:3000](http://localhost:3000) в браузере.

## Команды

### Разработка

```bash
pnpm dev          # Запуск dev сервера (localhost:3000)
pnpm build        # Сборка для production
pnpm start        # Запуск production сборки
```

### Качество кода

```bash
pnpm lint         # Проверка ESLint
pnpm typecheck    # Проверка типов TypeScript
```

### Через Makefile (из корня проекта)

```bash
make frontend-install    # Установка зависимостей
make frontend-dev        # Запуск dev сервера
make frontend-build      # Сборка production
make frontend-lint       # Линтинг
make frontend-typecheck  # Проверка типов
```

## Структура проекта

```
frontend/
├── pages/                  # Next.js Pages Router
│   ├── _app.tsx           # Обертка приложения
│   ├── _document.tsx      # HTML документ
│   └── index.tsx          # Главная страница
├── components/            # React компоненты
│   └── ui/               # shadcn/ui базовые компоненты
├── lib/                  # Утилиты и helpers
│   └── utils.ts          # cn() и другие утилиты
├── types/                # TypeScript типы
│   ├── api.ts            # Типы для API
│   └── index.ts          # Реэкспорт типов
├── styles/               # Глобальные стили
│   └── globals.css       # Tailwind directives + CSS variables
├── public/               # Статические файлы
├── doc/                  # Документация
│   ├── adr/             # Architecture Decision Records
│   ├── plans/           # Планы спринтов
│   ├── front-vision.md  # Техническое видение frontend
│   └── ...
└── reference/            # Референсы дизайна
```

## Работа с shadcn/ui

### Добавление компонентов

shadcn/ui использует подход copy-paste компонентов. Для добавления нового компонента:

```bash
pnpm dlx shadcn@latest add [component-name]
```

Примеры:

```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add card
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add dropdown-menu
```

Компоненты будут скопированы в `components/ui/`.

### Модификация компонентов

Все компоненты shadcn/ui находятся в исходном коде проекта (`components/ui/`), поэтому их можно свободно модифицировать под нужды проекта.

### Использование компонентов

```typescript
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function MyPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Hello World</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>Click me</Button>
      </CardContent>
    </Card>
  );
}
```

## Стилизация

### Tailwind CSS

Используется utility-first подход:

```typescript
<div className="flex items-center justify-center p-4 bg-primary text-primary-foreground rounded-lg">
  Content
</div>
```

### Dark Mode

Dark mode настроен через class-based подход:

```typescript
<div className="bg-white dark:bg-gray-900">
  Content
</div>
```

### CSS Variables

Для кастомизации цветов используются CSS переменные в `styles/globals.css`:

```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

## TypeScript

Проект использует TypeScript в strict mode. Все компоненты, функции и переменные должны быть типизированы.

### Path Aliases

Используется алиас `@/*` для импортов:

```typescript
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { DashboardStats } from "@/types";
```

### Проверка типов

```bash
pnpm tsc --noEmit
```

## API Integration

### Переменные окружения

API URL настраивается через переменную окружения:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Типы API

Все типы для API определены в `types/api.ts` на основе контракта backend API.

```typescript
import type { DashboardStats, Period } from "@/types";

const stats: DashboardStats = await fetchStats("7d");
```

## Документация

- [Техническое видение](doc/front-vision.md) - принципы разработки и архитектура
- [ADR 0001](doc/adr/0001-frontend-tech-stack.md) - обоснование выбора технологий
- [Функциональные требования](doc/dashboard-requirements.md) - требования к дашборду

## Roadmap

См. [Frontend Roadmap](../docs/frontend-roadmap.md) для плана развития.

## Соглашения

- **Компоненты:** PascalCase (`Button.tsx`, `MetricCard.tsx`)
- **Утилиты:** camelCase (`utils.ts`, `formatters.ts`)
- **Типы:** PascalCase (`DashboardStats`, `MetricCardProps`)
- **CSS классы:** Tailwind utility classes
- **Коммиты:** на русском языке (`feat: добавлен компонент MetricCard`)

## Troubleshooting

### pnpm: command not found

Установите pnpm глобально:

```bash
npm install -g pnpm
```

### Module not found

Убедитесь что зависимости установлены:

```bash
pnpm install
```

### TypeScript errors

Проверьте что `tsconfig.json` настроен правильно и запустите проверку типов:

```bash
pnpm tsc --noEmit
```

## Лицензия

ISC

