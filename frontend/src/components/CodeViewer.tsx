import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { ReviewFinding } from '../types';

interface CodeViewerProps {
    code: string;
    language?: string;
    findings: ReviewFinding[];
}

export function CodeViewer({ code, language = 'python', findings }: CodeViewerProps) {
    // Map line numbers to finding severities for highlighting
    const lineDecorations = new Map<number, string>();
    findings.forEach(f => {
        if (f.line_number) {
            // prioritize critical
            if (f.severity === 'critical') lineDecorations.set(f.line_number, 'bg-red-500/20 border-l-4 border-red-500');
            else if (f.severity === 'warning' && !lineDecorations.has(f.line_number))
                lineDecorations.set(f.line_number, 'bg-yellow-500/10 border-l-4 border-yellow-500');
            else if (!lineDecorations.has(f.line_number))
                lineDecorations.set(f.line_number, 'bg-blue-500/10 border-l-4 border-blue-500');
        }
    });

    return (
        <div className="rounded-md overflow-hidden bg-[#1e1e1e] border border-border text-sm relative">
            <SyntaxHighlighter
                language={language}
                style={vscDarkPlus}
                showLineNumbers={true}
                wrapLines={true}
                lineProps={(lineNumber: number) => {
                    const style = lineDecorations.get(lineNumber);
                    if (style) {
                        return { className: `block w-full ${style}` };
                    }
                    return {};
                }}
                customStyle={{ margin: 0, padding: '1.5rem', background: 'transparent' }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
}
