export type Severity = "critical" | "warning" | "info";
export type Category = "security" | "performance" | "quality" | "other";

export interface ReviewFinding {
    id: string; // generated client side or generic
    category: Category;
    severity: Severity;
    line_number: number | null;
    description: string;
    suggestion: string;
    agent_source: string;
}

export interface FinalReview {
    file_path: string;
    summary: string;
    overall_score: number;
    all_findings: ReviewFinding[];
}
