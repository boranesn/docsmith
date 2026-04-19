import asyncio
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Watch a repository and re-generate docs on file changes.")
console = Console()


@app.callback(invoke_without_command=True)
def watch(
    repo: str = typer.Argument(..., help="Local path to the repository."),
    output: Path = typer.Option(Path("./docs"), "--output", "-o"),
) -> None:
    """Watch for changes and incrementally re-generate documentation."""
    from watchfiles import awatch

    from docsmith.agents.graph import run_pipeline
    from docsmith.ingestion.walker import iter_source_files

    console.print(f"[bold green]docsmith watch[/bold green] → [cyan]{repo}[/cyan]")
    console.print("Watching for changes... (Ctrl+C to stop)\n")

    async def _watch() -> None:
        async for changes in awatch(repo):
            changed_files = {str(Path(p).resolve()) for _, p in changes}
            console.print(f"[yellow]Changed:[/yellow] {len(changed_files)} file(s)")
            await run_pipeline(repo_path=repo, output_path=output, changed_files=changed_files)
            console.print("[green]Docs updated.[/green]\n")

    asyncio.run(_watch())
