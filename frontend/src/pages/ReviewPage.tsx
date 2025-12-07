import { useLocation, Navigate } from "react-router-dom";
import type { FinalReview } from "../types";
import { CodeViewer } from "../components/CodeViewer";
import { FindingCard } from "../components/FindingCard";
import { ScoreBadge } from "../components/ScoreBadge";
import { useState } from "react";
import { clsx } from "clsx";
import { Shield, Zap, CheckCircle } from "lucide-react";

export function ReviewPage() {
    const { state } = useLocation();
    const [filter, setFilter] = useState<"all" | "security" | "performance" | "quality">("all");

    if (!state || !state.result) {
        return <Navigate to="/" />;
    }

    const result = state.result as FinalReview;
    const code = state.code as string;

    console.log("Review Result:", result); // Debugging

    const filteredFindings = result.all_findings.filter(f => {
        if (filter === "all") return true;
        const normalizedFilter = filter.toLowerCase();
        const catMatches = f.category?.toLowerCase() === normalizedFilter;
        const sourceMatches = f.agent_source?.toLowerCase().includes(normalizedFilter);
        return catMatches || sourceMatches;
    }).sort((a, b) => {
        // Sort by line number (nulls last)
        const lineA = a.line_number ?? Number.MAX_SAFE_INTEGER;
        const lineB = b.line_number ?? Number.MAX_SAFE_INTEGER;
        if (lineA !== lineB) {
            return lineA - lineB;
        }
        // If same line, sort by severity (critical > warning > info)
        const severityOrder: Record<string, number> = {
            "critical": 0, "warning": 1, "info": 2
        };
        const sevA = severityOrder[a.severity.toLowerCase()] ?? 3;
        const sevB = severityOrder[b.severity.toLowerCase()] ?? 3;
        return sevA - sevB;
    });

    return (
        <div className="min-h-screen bg-background flex flex-col">
            {/* Header */}
            <header className="border-b bg-card px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-bold">Review Report</h1>
                    <span className="text-sm text-muted-foreground hidden md:inline">{result.file_path}</span>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right mr-2 hidden md:block">
                        <span className="block text-xs text-muted-foreground uppercase font-bold">Overall Score</span>
                    </div>
                    <ScoreBadge score={result.overall_score} />
                </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
                {/* Sidebar Findings */}
                <aside className="w-1/3 min-w-[350px] border-r bg-secondary/5 flex flex-col overflow-hidden">
                    <div className="p-4 border-b space-y-4">
                        <div className="bg-secondary/10 p-4 rounded-lg border border-border shadow-sm">
                            <h3 className="font-bold text-sm uppercase text-muted-foreground mb-2">Executive Summary</h3>
                            <p className="text-sm leading-relaxed text-foreground">{result.summary}</p>
                        </div>

                        {/* Filters */}
                        <div className="flex gap-2">
                            <button onClick={() => setFilter("all")} className={clsx("flex-1 py-1.5 text-xs font-medium rounded border transition-colors", filter === "all" ? "bg-primary text-primary-foreground border-primary" : "bg-secondary text-secondary-foreground border-secondary hover:bg-secondary/80")}>All</button>
                            <button onClick={() => setFilter("security")} className={clsx("p-2 rounded border transition-colors", filter === "security" ? "bg-red-500 text-white border-red-500" : "bg-secondary text-secondary-foreground border-secondary hover:bg-secondary/80")} title="Security"><Shield className="w-4 h-4" /></button>
                            <button onClick={() => setFilter("performance")} className={clsx("p-2 rounded border transition-colors", filter === "performance" ? "bg-purple-500 text-white border-purple-500" : "bg-secondary text-secondary-foreground border-secondary hover:bg-secondary/80")} title="Performance"><Zap className="w-4 h-4" /></button>
                            <button onClick={() => setFilter("quality")} className={clsx("p-2 rounded border transition-colors", filter === "quality" ? "bg-green-500 text-white border-green-500" : "bg-secondary text-secondary-foreground border-secondary hover:bg-secondary/80")} title="Quality"><CheckCircle className="w-4 h-4" /></button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {filteredFindings.map((f, i) => (
                            <FindingCard key={i} finding={f} />
                        ))}
                        {filteredFindings.length === 0 && (
                            <div className="text-center py-10 text-muted-foreground">
                                <CheckCircle className="w-10 h-10 mx-auto mb-2 opacity-50" />
                                <p>No findings for this category.</p>
                            </div>
                        )}
                    </div>
                </aside>

                {/* Code View */}
                <main className="flex-1 overflow-y-auto p-6 bg-[#1e1e1e]">
                    <CodeViewer code={code} findings={result.all_findings} />
                </main>
            </div>
        </div>
    );
}
