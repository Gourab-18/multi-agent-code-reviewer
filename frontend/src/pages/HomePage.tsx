import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";

import { Upload, CheckCircle, Loader2 } from "lucide-react";
import { api } from "../api/client";
import { clsx } from "clsx";

export function HomePage() {
    const navigate = useNavigate();
    const [code, setCode] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleAnalyze = async () => {
        if (!code.trim()) return;
        setIsAnalyzing(true);
        try {
            const result = await api.reviewCode(code);
            // In a real app we would store full result in state context or fetch by ID
            // For MVP passing via state to review page
            navigate("/review/latest", { state: { result, code } });
        } catch (e) {
            alert("Analysis failed: " + e);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            const text = await file.text();
            setCode(text);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        maxFiles: 1,
        accept: { 'text/x-python': ['.py'], 'text/javascript': ['.js', '.jsx', '.ts', '.tsx'] }
    });

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
            <div className="max-w-4xl w-full space-y-8">
                <div className="text-center space-y-4">
                    <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent pb-1">
                        Multi-Agent Code Reviewer
                    </h1>
                    <p className="text-xl text-muted-foreground">
                        Get expert feedback from dedicated Security, Performance, and Quality AI agents.
                    </p>
                </div>

                <div className="bg-card border border-border rounded-xl shadow-2xl overflow-hidden p-6 space-y-6">
                    <div
                        {...getRootProps()}
                        className={clsx(
                            "border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors",
                            isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                        )}
                    >
                        <input {...getInputProps()} />
                        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                        <p className="text-lg font-medium">Drag & drop a file here, or click to select</p>
                        <p className="text-sm text-muted-foreground mt-2">Supports .py, .js, .ts</p>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-card px-2 text-muted-foreground">Or paste code</span>
                        </div>
                    </div>

                    <textarea
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        placeholder="def messy_function(data): ..."
                        className="w-full h-64 p-4 rounded-md bg-secondary/20 border border-input focus:ring-2 focus:ring-primary font-mono text-sm resize-y"
                    />

                    <button
                        onClick={handleAnalyze}
                        disabled={isAnalyzing || !code.trim()}
                        className="w-full py-4 bg-primary text-primary-foreground rounded-lg font-bold text-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="animate-spin" /> Analyzing with 3 Agents...
                            </>
                        ) : (
                            <>
                                <CheckCircle /> Start Review
                            </>
                        )}
                    </button>
                </div>

            </div>
        </div>
    );
}
