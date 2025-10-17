import { type FC } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { formatDate } from "@/lib/utils";
import { TimeSeriesPoint } from "@/types/api";

interface TimeSeriesChartProps {
    data: TimeSeriesPoint[];
}

export const TimeSeriesChart: FC<TimeSeriesChartProps> = ({ data }) => {
    const formattedData = data.map((point) => ({
        ...point,
        formattedDate: formatDate(point.date),
    }));

    return (
        <ResponsiveContainer width="100%" height={350}>
            <LineChart
                data={formattedData}
                margin={{
                    top: 5,
                    right: 10,
                    left: 10,
                    bottom: 0,
                }}
            >
                <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                    vertical={false}
                />
                <XAxis
                    dataKey="formattedDate"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                />
                <YAxis
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}`}
                />
                <Tooltip
                    contentStyle={{
                        backgroundColor: "hsl(var(--background))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "6px",
                    }}
                    labelStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Line
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{
                        r: 4,
                        fill: "hsl(var(--primary))",
                    }}
                />
            </LineChart>
        </ResponsiveContainer>
    );
};

