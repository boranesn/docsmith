import asyncio
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Re-generate docs only for symbols changed since a git ref.")
console = Console()


@app.callback(invoke_without_command=True)
def diff(
    repo: str = typer.Argument(..., help="Local path to the repository."),
    since: str = typer.Option("HEAD~1", "--since", help="Git ref to diff against."),
    output: Path = typer.Option(Path("./docs"), "--output", "-o"),
) -> None:
    """Incrementally update docs for changed symbols only."""
    from docsmith.agents.graph import run_pipeline
    from docsmith.analysis.diff import changed_files_since

    changed = changed_files_since(repo_path=repo, since=since)
    if not changed:
        console.print("[green]No source files changed.[/green]")
        raise typer.Exit()

    console.print(f"[bold]Changed files since {since}:[/bold]")
    for f in sorted(changed):
        console.print(f"  [cyan]{f}[/cyan]")

    asyncio.run(run_pipeline(repo_path=repo, output_path=output, changed_files=changed))
    console.print(f"\n[bold green]✓[/bold green] Incremental docs updated → [yellow]{output}[/yellow]")
