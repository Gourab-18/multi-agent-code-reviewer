import typer
import os
import uvicorn
import glob
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from dotenv import load_dotenv

from src.graph.workflow import ReviewOrchestrator
from src.rag.codebase_indexer import CodebaseIndexer
from src.rag.knowledge_base import KnowledgeBaseBuilder
from src.models.schemas import FinalReview

load_dotenv()

app = typer.Typer(help="Multi-Agent Code Reviewer CLI")
console = Console()

def _display_review(review: FinalReview, code_snippet: str = None):
    """Helper to display a single review nicely."""
    console.print(f"\n[bold underline]Review for: {review.file_path}[/bold underline]")
    console.print(f"Overall Score: [bold cyan]{review.overall_score}/10[/bold cyan]\n")
    
    console.print(Panel(review.summary, title="Executive Summary", border_style="blue"))
    
    # Sort findings
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    findings = sorted(review.all_findings, key=lambda x: severity_order.get(x.severity, 3))
    
    for f in findings:
        color = "red" if f.severity == "critical" else "yellow" if f.severity == "warning" else "blue"
        title = f"[{color} bold]{f.severity.upper()}[/{color} bold] - {f.category.upper()}"
        
        content = f"[bold]Issue:[/bold] {f.description}\n[bold]Fix:[/bold] {f.suggestion}\n"
        if f.agent_source:
             content += f"[italic dim]Detected by: {f.agent_source}[/italic dim]"
             
        # If line number exists and we have code, show snippet (simplified)
        # Note: robust implementation would slice lines around the error
        
        console.print(Panel(content, title=title, border_style=color))

@app.command()
def review(file_path: str):
    """
    Review a single source file.
    """
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' not found.")
        raise typer.Exit(code=1)
        
    orchestrator = ReviewOrchestrator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Reviewing {file_path}...", total=None)
        
        try:
            review_result = orchestrator.review_file(file_path)
            # Read snippet for display context (first 500 chars for now, or just pass None)
            with open(file_path, "r") as f:
                code_snippet = f.read()
            _display_review(review_result, code_snippet)
        except Exception as e:
            console.print(f"[bold red]Review Failed:[/bold red] {e}")


@app.command(name="review-dir")
def review_directory(directory: str, pattern: str = "**/*.py", json_output: bool = False):
    """
    Review a directory of files properly.
    """
    if not os.path.exists(directory):
        console.print(f"[bold red]Error:[/bold red] Directory '{directory}' not found.")
        raise typer.Exit(code=1)
        
    search_pattern = os.path.join(directory, pattern)
    files = glob.glob(search_pattern, recursive=True)
    
    if not files:
        console.print("[yellow]No files matches found.[/yellow]")
        return
        
    console.print(f"[bold]Found {len(files)} files to review.[/bold]")
    
    orchestrator = ReviewOrchestrator()
    results = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Reviewing files...", total=len(files))
        
        for file in files:
            if os.path.isdir(file): continue
            
            try:
                # We could run this in parallel but let's keep it sequential for safety/rate limits
                res = orchestrator.review_file(file)
                results.append(res)
            except Exception as e:
                console.print(f"[red]Failed to review {file}: {e}[/red]")
            
            progress.advance(task)
            
    # Summary Table
    table = Table(title="Review Summary")
    table.add_column("File", style="cyan")
    table.add_column("Score", style="magenta")
    table.add_column("Crit/Warn/Info", style="green")
    
    for res in results:
        counts = {"critical": 0, "warning": 0, "info": 0}
        for f in res.all_findings:
            if f.severity in counts: counts[f.severity] += 1
            
        summary_counts = f"{counts['critical']}/{counts['warning']}/{counts['info']}"
        table.add_row(res.file_path, str(res.overall_score), summary_counts)
        
    console.print(table)
    
    if json_output:
        import json
        save_path = "review_report.json"
        with open(save_path, "w") as f:
            json.dump([r.dict() for r in results], f, indent=2, default=str)
        console.print(f"Report saved to {save_path}")

@app.command()
def index_codebase(directory: str):
    """
    Index a local codebase for RAG context.
    """
    indexer = CodebaseIndexer()
    indexer.index_repo(directory)
    console.print("[green]Codebase indexed successfully.[/green]")

@app.command()
def rebuild_kb():
    """
    Rebuild the best practices knowledge base.
    """
    builder = KnowledgeBaseBuilder()
    builder.build()
    console.print("[green]Knowledge base rebuilt successfully.[/green]")

@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Start the API server.
    """
    console.print(f"[green]Starting server at http://{host}:{port}[/green]")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    app()
