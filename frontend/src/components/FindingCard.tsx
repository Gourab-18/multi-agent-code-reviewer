import type { ReviewFinding } from "../types";
import { AgentAvatar } from "./AgentAvatar";
import { clsx } from "clsx";

interface FindingCardProps {
    finding: ReviewFinding;
    compact?: boolean;
}

export function FindingCard({ finding, compact = false }: FindingCardProps) {
    const isCrit = finding.severity === "critical";
    const isWarn = finding.severity === "warning";

    const borderColor = isCrit
        ? "border-red-500/50 bg-red-500/5"
        : isWarn
            ? "border-yellow-500/50 bg-yellow-500/5"
            : "border-blue-400/30 bg-blue-500/5";

    return (
        <div className={clsx("rounded-lg border p-4 transition-all hover:bg-accent/5", borderColor)}>
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    {finding.agent_source && (
                        <AgentAvatar agent={finding.agent_source} className="w-6 h-6 p-1" />
                    )}
                    <span className="text-xs font-mono uppercase tracking-wider text-muted-foreground">
                        {finding.category}
                    </span>
                </div>
                <span
                    className={clsx(
                        "text-xs font-bold px-2 py-0.5 rounded uppercase",
                        isCrit ? "bg-red-500 text-white" : isWarn ? "bg-yellow-500 text-black" : "bg-blue-500 text-white"
                    )}
                >
                    {finding.severity}
                </span>
            </div>

            <div className="mb-2">
                <p className="font-medium text-sm leading-relaxed text-foreground">{finding.description}</p>
                {finding.line_number && (
                    <span className="text-xs text-muted-foreground mt-1 block">Line {finding.line_number}</span>
                )}
            </div>

            {!compact && finding.suggestion && (
                <div className="mt-3 bg-background/50 p-2 rounded text-sm font-mono text-muted-foreground border border-border/50">
                    <span className="block text-xs uppercase font-bold text-green-600 mb-1">Fix Suggestion:</span>
                    {finding.suggestion}
                </div>
            )}
        </div>
    );
}
