import { clsx } from "clsx";

interface ScoreBadgeProps {
    score: number;
    size?: "sm" | "md" | "lg";
}

export function ScoreBadge({ score, size = "md" }: ScoreBadgeProps) {
    let color = "bg-red-500";
    if (score >= 9) color = "bg-green-500";
    else if (score >= 7) color = "bg-blue-500";
    else if (score >= 5) color = "bg-yellow-500";
    else if (score >= 3) color = "bg-orange-500";

    const sizeClasses = {
        sm: "w-8 h-8 text-sm",
        md: "w-12 h-12 text-lg",
        lg: "w-20 h-20 text-3xl",
    };

    return (
        <div
            className={clsx(
                "rounded-full flex items-center justify-center font-bold text-white shadow-lg",
                color,
                sizeClasses[size]
            )}
        >
            {score.toFixed(1)}
        </div>
    );
}
