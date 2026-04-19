from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Serve generated docs via a local dev server.")
console = Console()


@app.callback(invoke_without_command=True)
def serve(
    docs_dir: Path = typer.Argument(Path("./docs"), help="Directory containing generated docs."),
    port: int = typer.Option(8080, "--port", "-p"),
    host: str = typer.Option("127.0.0.1", "--host"),
) -> None:
    """Serve documentation locally with FastAPI."""
    import uvicorn

    from docsmith.renderers.server import create_app

    if not docs_dir.exists():
        console.print(f"[red]Docs directory not found:[/red] {docs_dir}")
        raise typer.Exit(1)

    fastapi_app = create_app(docs_dir)
    console.print(f"[bold green]docsmith serve[/bold green] → http://{host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, log_level="warning")
