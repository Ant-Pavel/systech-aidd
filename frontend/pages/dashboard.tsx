import { useState, useEffect } from "react";
import Head from "next/head";
import Link from "next/link";
import { MessageSquare } from "lucide-react";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { TimeSeriesChart } from "@/components/dashboard/TimeSeriesChart";
import { PeriodSelector } from "@/components/dashboard/PeriodSelector";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats, Period } from "@/types/api";

export default function Dashboard() {
    const [selectedPeriod, setSelectedPeriod] = useState<Period>("7d");
    const [data, setData] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const stats = await fetchDashboardStats(selectedPeriod);
                setData(stats);
            } catch (err) {
                setError(
                    err instanceof Error
                        ? err.message
                        : "Failed to load dashboard data"
                );
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [selectedPeriod]);

    return (
        <>
            <Head>
                <title>Dashboard - Systech AIDD</title>
                <meta
                    name="description"
                    content="Statistics dashboard for AI-Driven Dialogue System"
                />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            <main className="min-h-screen bg-background">
                <div className="container mx-auto px-4 py-8">
                    <header className="mb-8">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h1 className="text-3xl font-bold tracking-tight">
                                    Dashboard статистики диалогов
                                </h1>
                                <p className="text-muted-foreground mt-1">
                                    Мониторинг активности Telegram-бота
                                </p>
                            </div>
                            <div className="flex items-center gap-2">
                                <Link href="/chat">
                                    <Button variant="outline" size="icon">
                                        <MessageSquare className="h-5 w-5" />
                                    </Button>
                                </Link>
                                <ThemeToggle />
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <PeriodSelector
                                selectedPeriod={selectedPeriod}
                                onPeriodChange={setSelectedPeriod}
                            />
                        </div>
                    </header>

                    {loading && (
                        <div className="flex items-center justify-center py-12">
                            <div className="text-center">
                                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
                                <p className="mt-4 text-muted-foreground">
                                    Загрузка данных...
                                </p>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
                            <p className="text-sm font-medium text-destructive">
                                Ошибка: {error}
                            </p>
                            <p className="text-sm text-muted-foreground mt-1">
                                Убедитесь, что backend запущен (python api_main.py)
                            </p>
                        </div>
                    )}

                    {data && !loading && (
                        <>
                            {/* Metric Cards */}
                            <div className="grid gap-4 md:grid-cols-3 mb-8">
                                <MetricCard
                                    title="Total Messages"
                                    value={data.metrics.total_messages.value}
                                    changePercent={
                                        data.metrics.total_messages.change_percent
                                    }
                                    trend={data.metrics.total_messages.trend}
                                    description={
                                        data.metrics.total_messages.description
                                    }
                                />
                                <MetricCard
                                    title="Active Conversations"
                                    value={data.metrics.active_conversations.value}
                                    changePercent={
                                        data.metrics.active_conversations
                                            .change_percent
                                    }
                                    trend={data.metrics.active_conversations.trend}
                                    description={
                                        data.metrics.active_conversations.description
                                    }
                                />
                                <MetricCard
                                    title="Avg Conversation Length"
                                    value={
                                        data.metrics.avg_conversation_length.value
                                    }
                                    changePercent={
                                        data.metrics.avg_conversation_length
                                            .change_percent
                                    }
                                    trend={data.metrics.avg_conversation_length.trend}
                                    description={
                                        data.metrics.avg_conversation_length
                                            .description
                                    }
                                />
                            </div>

                            {/* Chart */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Messages Over Time</CardTitle>
                                    <CardDescription>
                                        Динамика количества сообщений за выбранный период
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="pl-2">
                                    <TimeSeriesChart data={data.time_series} />
                                </CardContent>
                            </Card>
                        </>
                    )}
                </div>
            </main>
        </>
    );
}

