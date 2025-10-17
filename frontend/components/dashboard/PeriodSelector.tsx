import { type FC } from "react";
import { Button } from "@/components/ui/button";
import { Period } from "@/types/api";

interface PeriodSelectorProps {
    selectedPeriod: Period;
    onPeriodChange: (period: Period) => void;
}

const periods: { value: Period; label: string }[] = [
    { value: "7d", label: "Last 7 days" },
    { value: "30d", label: "Last 30 days" },
    { value: "3m", label: "Last 3 months" },
];

export const PeriodSelector: FC<PeriodSelectorProps> = ({
    selectedPeriod,
    onPeriodChange,
}) => {
    return (
        <div className="flex items-center gap-2">
            {periods.map((period) => (
                <Button
                    key={period.value}
                    variant={
                        selectedPeriod === period.value ? "secondary" : "ghost"
                    }
                    size="sm"
                    onClick={() => onPeriodChange(period.value)}
                >
                    {period.label}
                </Button>
            ))}
        </div>
    );
};

