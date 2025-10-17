/**
 * API types for backend communication
 * Based on dashboard requirements and Mock API contract
 */

export interface MetricCard {
    value: number;
    change_percent: number;
    trend: "up" | "down" | "stable";
    description: string;
}

export interface TimeSeriesPoint {
    date: string; // ISO 8601 format (YYYY-MM-DD)
    value: number;
}

export interface DashboardStats {
    metrics: {
        total_messages: MetricCard;
        active_conversations: MetricCard;
        avg_conversation_length: MetricCard;
    };
    time_series: TimeSeriesPoint[];
}

export type Period = "7d" | "30d" | "3m";

