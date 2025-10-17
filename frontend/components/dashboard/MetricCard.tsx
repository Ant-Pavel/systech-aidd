import { type FC } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatNumber, getTrendColor } from "@/lib/utils";

interface MetricCardProps {
    title: string;
    value: number;
    changePercent: number;
    trend: "up" | "down" | "stable";
    description: string;
}

export const MetricCard: FC<MetricCardProps> = ({
    title,
    value,
    changePercent,
    trend,
    description,
}) => {
    const isDecimal = title.toLowerCase().includes("avg");
    const formattedValue = formatNumber(value, isDecimal ? 1 : 0);
    const trendColor = getTrendColor(trend);

    const TrendIcon =
        trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                <TrendIcon className={`h-4 w-4 ${trendColor}`} />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{formattedValue}</div>
                <div className="flex items-center gap-2 mt-2">
                    <Badge
                        variant={
                            trend === "up"
                                ? "default"
                                : trend === "down"
                                    ? "destructive"
                                    : "secondary"
                        }
                        className="text-xs"
                    >
                        {changePercent > 0 ? "+" : ""}
                        {changePercent.toFixed(1)}%
                    </Badge>
                    <CardDescription className="text-xs">
                        {description}
                    </CardDescription>
                </div>
            </CardContent>
        </Card>
    );
};

