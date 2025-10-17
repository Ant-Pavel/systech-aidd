# Техническое видение Frontend приложения

## 1. Технологии

### Основные технологии
- **Next.js 14+** - React фреймворк с Pages Router
- **React 18+** - библиотека для построения пользовательских интерфейсов
- **TypeScript 5+** - типизированный JavaScript для безопасности типов
- **pnpm** - быстрый и эффективный пакетный менеджер
- **Tailwind CSS 3+** - utility-first CSS фреймворк
- **shadcn/ui** - коллекция переиспользуемых компонентов на базе Radix UI

### Инструменты качества кода
- **ESLint** - линтер для JavaScript/TypeScript
- **TypeScript Compiler** - проверка типов (strict mode)
- **Prettier** (опционально) - форматирование кода

### Дополнительные библиотеки
- **Radix UI** - примитивы для доступных компонентов (через shadcn/ui)
- **class-variance-authority (cva)** - управление вариантами стилей компонентов
- **clsx** / **tailwind-merge** - утилиты для работы с CSS классами

## 2. Принципы разработки

### Основные принципы
- **TypeScript-first** - строгая типизация везде, strict mode
- **Component-Driven Development** - модульный компонентный подход
- **KISS (Keep It Simple, Stupid)** - максимальная простота, никакого оверинжиниринга
- **Composition over Configuration** - композиция компонентов вместо сложных конфигураций
- **Accessibility First** - доступность интерфейса для всех пользователей

### Подход к коду
- **Функциональные компоненты** - только React функциональные компоненты с хуками
- **TypeScript везде** - все компоненты, функции, пропсы типизированы
- **Именованные экспорты** - для компонентов и утилит (кроме страниц Next.js)
- **Colocation** - размещение связанных файлов рядом
- **Минимум зависимостей** - добавляем только необходимые пакеты

### UI/UX подход
- **Mobile-first** - адаптивный дизайн с приоритетом мобильных устройств
- **Dark mode ready** - поддержка темной темы (через Tailwind и shadcn/ui)
- **Консистентность** - единообразие компонентов и паттернов
- **Feedback** - визуальная обратная связь на действия пользователя

## 3. Структура проекта

```
frontend/
├── pages/                  # Next.js Pages Router
│   ├── _app.tsx           # Обертка приложения (providers, layouts)
│   ├── _document.tsx      # HTML документ (head, body)
│   ├── index.tsx          # Главная страница (дашборд)
│   └── api/               # API routes (если нужны)
├── components/            # React компоненты
│   ├── ui/               # shadcn/ui базовые компоненты (Button, Card, etc.)
│   ├── dashboard/        # Компоненты дашборда (MetricCard, TimeSeriesChart)
│   └── layout/           # Layout компоненты (Header, Footer, Sidebar)
├── lib/                  # Утилиты и helpers
│   ├── utils.ts          # Общие утилиты (cn, formatters)
│   └── api.ts            # API клиент для backend (на будущее)
├── types/                # TypeScript типы и интерфейсы
│   ├── api.ts            # Типы для API responses
│   └── index.ts          # Реэкспорт типов
├── styles/               # Глобальные стили
│   └── globals.css       # Tailwind directives + custom styles
├── public/               # Статические файлы (images, fonts)
├── doc/                  # Документация
│   ├── adr/             # Architecture Decision Records
│   └── plans/           # Планы спринтов
└── reference/            # Референсы дизайна
```

### Принципы организации файлов

- **Pages** - только страницы Next.js, минимум логики
- **Components** - переиспользуемые UI компоненты
- **Lib** - утилиты, хелперы, API клиенты
- **Types** - все TypeScript типы и интерфейсы
- **Styles** - глобальные стили и Tailwind конфигурация

## 4. Соглашения по именованию

### Файлы и директории
- **Компоненты**: PascalCase (`Button.tsx`, `MetricCard.tsx`)
- **Утилиты**: camelCase (`utils.ts`, `formatters.ts`)
- **Типы**: camelCase (`api.ts`, `dashboard.ts`)
- **Директории**: kebab-case (`dashboard-stats/`, `metric-card/`)
- **Страницы Next.js**: kebab-case (`index.tsx`, `dashboard.tsx`)

### Код
- **Компоненты**: PascalCase (`MetricCard`, `TimeSeriesChart`)
- **Функции**: camelCase (`formatDate`, `fetchStats`)
- **Константы**: UPPER_SNAKE_CASE (`API_BASE_URL`, `MAX_RETRIES`)
- **Типы/Интерфейсы**: PascalCase (`DashboardStats`, `MetricCardProps`)
- **Переменные**: camelCase (`userData`, `isLoading`)

### Структура компонента

```typescript
// MetricCard.tsx
import { type FC } from "react";
import { Card } from "@/components/ui/card";

interface MetricCardProps {
  title: string;
  value: number;
  changePercent: number;
  trend: "up" | "down" | "stable";
}

export const MetricCard: FC<MetricCardProps> = ({
  title,
  value,
  changePercent,
  trend,
}) => {
  return (
    <Card>
      {/* Component implementation */}
    </Card>
  );
};
```

## 5. Стилизация с Tailwind CSS и shadcn/ui

### Tailwind CSS
- **Utility-first подход** - использование утилитарных классов
- **Responsive design** - mobile-first брейкпоинты (`sm:`, `md:`, `lg:`, `xl:`)
- **Dark mode** - class-based (`dark:` prefix)
- **Кастомизация** - через `tailwind.config.ts`

### shadcn/ui
- **Copy-paste компоненты** - компоненты копируются в проект (не npm пакет)
- **Полный контроль** - можно модифицировать под нужды проекта
- **Radix UI primitives** - базируется на доступных примитивах
- **Tailwind стилизация** - стилизованы с помощью Tailwind

### Паттерн стилизации

```typescript
import { cn } from "@/lib/utils";

export const Component = ({ className, ...props }) => {
  return (
    <div
      className={cn(
        "base-styles",
        "responsive-styles md:flex-row",
        "dark:bg-gray-800",
        className
      )}
      {...props}
    />
  );
};
```

## 6. Управление состоянием

### Локальное состояние
- **useState** - для локального состояния компонента
- **useReducer** - для сложной логики состояния
- **Context API** - для состояния уровня приложения (theme, auth)

### Серверное состояние (будущее)
- **React Query** / **SWR** - для кеширования и синхронизации с API (если понадобится)
- **На данный момент** - простой fetch в компонентах

### Формы (будущее)
- **React Hook Form** - для сложных форм (если понадобится)
- **Zod** - валидация схем (если понадобится)

## 7. Работа с API

### Подход
- **NEXT_PUBLIC_API_URL** - переменная окружения для URL backend API
- **Fetch API** - нативный fetch для HTTP запросов
- **TypeScript типы** - строгая типизация request/response

### Пример API клиента (будущее)

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchDashboardStats(period: string): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE_URL}/api/stats?period=${period}`);
  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }
  return response.json();
}
```

## 8. TypeScript конфигурация

### Настройки tsconfig.json
- **strict: true** - строгий режим TypeScript
- **Path aliases** - `@/*` для импортов из корня проекта
- **JSX: preserve** - для Next.js
- **module: esnext** - современные модули
- **target: es5** - совместимость с браузерами

### Стиль типизации

```typescript
// Предпочитаем interface для пропсов компонентов
interface ButtonProps {
  variant: "primary" | "secondary";
  children: React.ReactNode;
}

// Type для объединений и утилитарных типов
type Status = "loading" | "success" | "error";

// Явные типы возврата
export function formatDate(date: Date): string {
  return date.toISOString();
}
```

## 9. Тестирование (будущее)

### Планируемый подход
- **Jest** - фреймворк тестирования
- **React Testing Library** - тестирование компонентов
- **Unit тесты** - для утилит и хелперов
- **Integration тесты** - для страниц и флоу
- **E2E тесты** - Playwright для критических путей (опционально)

### Coverage
- Минимум 70% coverage для компонентов и утилит
- Фокус на критическую функциональность

## 10. Performance и Optimization

### Next.js оптимизации
- **Static Generation (SSG)** - для статических страниц
- **Server-Side Rendering (SSR)** - при необходимости свежих данных
- **Image Optimization** - Next.js Image component
- **Code Splitting** - автоматически через dynamic imports

### React оптимизации
- **Lazy loading** - для тяжелых компонентов
- **Memo** - для дорогих вычислений и рендеров
- **useMemo / useCallback** - когда действительно нужно

### Принцип
> Сначала работающий код, потом оптимизация. Измеряем, затем оптимизируем.

## 11. Доступность (Accessibility)

### Принципы
- **Semantic HTML** - правильные HTML теги
- **ARIA attributes** - когда семантики недостаточно
- **Keyboard navigation** - полная навигация с клавиатуры
- **Screen reader support** - через shadcn/ui (Radix UI)
- **Color contrast** - соответствие WCAG 2.1 AA

### shadcn/ui
- Все компоненты shadcn/ui уже доступны по умолчанию
- Базируются на Radix UI с полной поддержкой a11y

## 12. Workflow разработки

### Команды
```bash
pnpm dev              # Запуск dev сервера (localhost:3000)
pnpm build            # Сборка для production
pnpm start            # Запуск production сборки
pnpm lint             # ESLint проверка
pnpm typecheck        # TypeScript проверка
```

### Перед коммитом
```bash
make frontend-lint        # Линтинг
make frontend-typecheck   # Проверка типов
make frontend-build       # Проверка сборки
```

## 13. Roadmap развития

### Phase 1: Инициализация (F-S2) ✅
- Настройка Next.js + TypeScript
- Интеграция shadcn/ui
- Базовая структура проекта

### Phase 2: Dashboard (F-S3)
- Реализация дашборда статистики
- Интеграция с Mock API
- Визуализация данных

### Phase 3: Chat UI (F-S4)
- Веб-интерфейс чата
- API для чата
- Админ функционал

### Phase 4: Real API (F-S5)
- Интеграция с реальным API
- Production deployment
- Оптимизация производительности

## 14. Принципы коммитов

### Формат
- **На русском языке**
- **Формат**: `<тип>: <описание>`
- **Типы**: feat, fix, refactor, test, docs, chore, style, ui

### Примеры
```
feat: добавлен компонент MetricCard для дашборда
ui: обновлен дизайн кнопок с использованием shadcn/ui
fix: исправлена типизация пропсов TimeSeriesChart
refactor: переработана структура компонентов dashboard
docs: обновлена документация по стилизации
```

## 15. Что избегать

### Антипаттерны
- ❌ Prop drilling - передача пропсов через много уровней (используй Context)
- ❌ Inline стили - используй Tailwind классы
- ❌ any типы - всегда типизируй правильно
- ❌ Большие компоненты - разбивай на меньшие
- ❌ Дублирование кода - выноси в переиспользуемые компоненты/утилиты

### Оверинжиниринг
- ❌ Не создавай абстракции "на будущее"
- ❌ Не добавляй библиотеки без реальной необходимости
- ❌ Не усложняй архитектуру преждевременно

## 16. Чеклист код-ревью

- [ ] TypeScript strict mode без ошибок
- [ ] Все компоненты типизированы
- [ ] Используются shadcn/ui компоненты где возможно
- [ ] Responsive дизайн (mobile-first)
- [ ] Доступность (semantic HTML, ARIA)
- [ ] ESLint проходит без ошибок
- [ ] Код читаемый и понятный
- [ ] Нет дублирования логики
- [ ] Компоненты небольшие и фокусные
- [ ] Документация обновлена

