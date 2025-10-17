<!-- d951da2b-dd49-4837-bcfa-d94a329c3bf7 dfbc961c-9209-464c-bfa6-18c89d293bf7 -->
# Спринт 3: Реализация Dashboard статистики диалогов

## Обзор

Реализовать дашборд для визуализации статистики диалогов Telegram-бота. Дашборд включает 3 метрические карточки (Total Messages, Active Conversations, Avg Conversation Length), график временного ряда и фильтрацию по периодам (7d, 30d, 3m). Интеграция с Mock API endpoint `/api/stats`.

## Архитектурное решение

**Референс**: shadcn/ui dashboard-01 block (dark theme, metric cards, chart)

**Компонентная структура**:

- `components/dashboard/MetricCard.tsx` - карточка метрики с трендом
- `components/dashboard/TimeSeriesChart.tsx` - график временного ряда (Recharts)
- `components/dashboard/PeriodSelector.tsx` - кнопки фильтрации периодов
- `lib/api.ts` - API клиент для запросов к backend
- `pages/dashboard.tsx` - страница дашборда
- `pages/index.tsx` - редирект на /dashboard

**Библиотека визуализации**: Recharts (совместима с Next.js/React, TypeScript-friendly)

## План реализации

### 1. Установка зависимостей

**Действие**: Добавить Recharts для графиков

```bash
cd frontend && pnpm add recharts
pnpm add -D @types/recharts
```

### 2. Добавление shadcn/ui компонентов

**Действие**: Добавить Badge компонент для индикаторов трендов

```bash
cd frontend && npx shadcn@latest add badge
```

### 3. Создание API клиента

**Файл**: `frontend/lib/api.ts`

**Содержание**:

```typescript
import { DashboardStats, Period } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchDashboardStats(period: Period): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE_URL}/api/stats?period=${period}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }
  return response.json();
}
```

### 4. Создание компонента MetricCard

**Файл**: `frontend/components/dashboard/MetricCard.tsx`

**Особенности**:

- Принимает props: title, value, changePercent, trend, description
- Использует `Card` из shadcn/ui
- Отображает trend arrow (↑/↓) и Badge с цветом (green для up, red для down, gray для stable)
- Форматирование чисел (toLocaleString для больших чисел, toFixed(1) для avg_conversation_length)

### 5. Создание компонента TimeSeriesChart

**Файл**: `frontend/components/dashboard/TimeSeriesChart.tsx`

**Особенности**:

- Использует `LineChart`, `Line`, `XAxis`, `YAxis`, `CartesianGrid`, `Tooltip`, `ResponsiveContainer` из Recharts
- Принимает props: data (TimeSeriesPoint[])
- Адаптивный размер (ResponsiveContainer)
- Форматирование дат на оси X (краткий формат: MM/DD)
- Стилизация под dark theme (цвета линий, сетки совместимы с Tailwind dark mode)

### 6. Создание компонента PeriodSelector

**Файл**: `frontend/components/dashboard/PeriodSelector.tsx`

**Особенности**:

- Принимает props: selectedPeriod, onPeriodChange
- 3 кнопки: "Last 7 days" (7d), "Last 30 days" (30d), "Last 3 months" (3m)
- Использует `Button` с variant="ghost" / variant="secondary" для активного
- Inline flex layout

### 7. Добавление helper функций

**Файл**: `frontend/lib/utils.ts`

**Действие**: Добавить функции форматирования

```typescript
export function formatNumber(num: number, decimals: number = 0): string {
  return num.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function getTrendColor(trend: "up" | "down" | "stable"): string {
  if (trend === "up") return "text-green-600 dark:text-green-400";
  if (trend === "down") return "text-red-600 dark:text-red-400";
  return "text-gray-600 dark:text-gray-400";
}
```

### 8. Создание страницы Dashboard

**Файл**: `frontend/pages/dashboard.tsx` (новый)

**Особенности**:

- useState для selectedPeriod (default: "7d")
- useState для data (DashboardStats | null)
- useState для loading, error
- useEffect для загрузки данных при изменении period
- Layout: заголовок, PeriodSelector, grid с 3 MetricCard, TimeSeriesChart
- Обработка состояний: loading spinner, error message, empty state

**Layout структура**:

```tsx
<main className="min-h-screen bg-background">
  <div className="container mx-auto px-4 py-8">
    <header className="mb-8">
      <h1>Dashboard статистики диалогов</h1>
      <PeriodSelector />
    </header>
    
    {/* 3 metric cards в grid */}
    <div className="grid gap-4 md:grid-cols-3 mb-8">
      <MetricCard title="Total Messages" {...data.metrics.total_messages} />
      <MetricCard title="Active Conversations" {...data.metrics.active_conversations} />
      <MetricCard title="Avg Conversation Length" {...data.metrics.avg_conversation_length} />
    </div>
    
    {/* Chart */}
    <Card>
      <CardHeader><CardTitle>Messages Over Time</CardTitle></CardHeader>
      <CardContent>
        <TimeSeriesChart data={data.time_series} />
      </CardContent>
    </Card>
  </div>
</main>
```

### 9. Редирект с главной страницы

**Файл**: `frontend/pages/index.tsx`

**Действие**: Реализовать редирект на `/dashboard`

**Содержание**:

```tsx
import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();
  
  useEffect(() => {
    router.replace("/dashboard");
  }, [router]);
  
  return null; // или loading spinner
}
```

### 10. Настройка переменных окружения

**Файл**: `frontend/.env.local` (создать если отсутствует)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Критерии приемки

- [ ] Дашборд доступен по роуту `/dashboard`
- [ ] Главная страница `/` редиректит на `/dashboard`
- [ ] Дашборд отображает 3 метрические карточки с корректными данными из API
- [ ] График временного ряда визуализирует данные по дням/неделям
- [ ] Переключение периодов (7d, 30d, 3m) обновляет все данные
- [ ] Обработаны состояния loading и error
- [ ] Адаптивный дизайн (responsive на mobile/tablet/desktop)
- [ ] TypeScript strict mode без ошибок
- [ ] ESLint проходит без предупреждений
- [ ] Dark mode поддержка корректна
- [ ] Интеграция с Mock API работает (при запущенном `python api_main.py`)

## Технические детали

**API endpoint**: `GET http://localhost:8000/api/stats?period={7d|30d|3m}`

**Ключевые файлы**:

- `frontend/components/dashboard/MetricCard.tsx` (новый)
- `frontend/components/dashboard/TimeSeriesChart.tsx` (новый)
- `frontend/components/dashboard/PeriodSelector.tsx` (новый)
- `frontend/lib/api.ts` (новый)
- `frontend/pages/dashboard.tsx` (новый)
- `frontend/pages/index.tsx` (обновить - редирект)
- `frontend/lib/utils.ts` (добавить helpers)

**Зависимости**: recharts, @types/recharts, shadcn/ui badge

### To-dos

- [ ] Установить Recharts и добавить Badge компонент из shadcn/ui
- [ ] Создать API клиент в lib/api.ts для запросов к /api/stats
- [ ] Добавить helper функции для форматирования (formatNumber, formatDate, getTrendColor)
- [ ] Реализовать компонент MetricCard с трендом и форматированием
- [ ] Создать TimeSeriesChart компонент с использованием Recharts
- [ ] Реализовать PeriodSelector для переключения периодов
- [ ] Создать pages/dashboard.tsx с полным дашбордом и интеграцией API
- [ ] Обновить pages/index.tsx с редиректом на /dashboard
- [ ] Создать .env.local с NEXT_PUBLIC_API_URL
- [ ] Протестировать дашборд с Mock API, проверить responsive и dark mode