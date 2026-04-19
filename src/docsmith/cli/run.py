import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

app = typer.Typer(help="Generate documentation for a repository.")
console = Console()


@app.callback(invoke_without_command=True)
def run(
    repo: str = typer.Argument(..., help="Local path or GitHub URL to the repository."),
    output: Path = typer.Option(Path("./docs"), "--output", "-o", help="Output directory for docs."),
    reset: bool = typer.Option(False, "--reset", help="Clear existing ChromaDB before run."),
) -> None:
    """Run the full documentation pipeline on a repository."""
    from docsmith.agents.graph import run_pipeline
    from docsmith.storage.state import StateManager

    state_mgr = StateManager()
    metadata = state_mgr.new_run(repo_path=repo, output_path=str(output))

    console.print(f"[bold green]docsmith[/bold green] → [cyan]{repo}[/cyan]")
    console.print(f"Output: [yellow]{output}[/yellow]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running agent pipeline...", total=None)

        async def _run() -> dict:
            return await run_pipeline(repo_path=repo, output_path=output, reset=reset)

        result = asyncio.run(_run())
        progress.update(task, description="[green]Done![/green]")

    metadata.quality_score = result.get("quality_score", 0.0)
    metadata.language_breakdown = result.get("language_breakdown", {})
    metadata.agent_trace = result.get("agent_trace", [])
    state_mgr.save(metadata)

    coverage = result.get("coverage")
    if coverage:
        pct = coverage.coverage_pct
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        console.print(f"\n[bold]Documentation Coverage:[/bold] {pct:.1f}%  {bar}")
        console.print(f"  Documented:   [green]{coverage.documented_symbols}[/green] symbols")
        console.print(f"  Missing docs: [red]{coverage.total_public_symbols - coverage.documented_symbols}[/red] symbols")

    console.print(f"\n[bold green]✓[/bold green] Docs written to [yellow]{output}[/yellow]")
