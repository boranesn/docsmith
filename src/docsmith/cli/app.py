import typer
from rich.console import Console

app = typer.Typer(
    name="docsmith",
    help="Autonomous multi-agent documentation generator for any codebase.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print("[bold]docsmith[/bold] v0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: B008
        False,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    pass


# Register sub-commands
from docsmith.cli import diff, run, serve, watch  # noqa: E402, F401

app.add_typer(run.app, name="run")
app.add_typer(watch.app, name="watch")
app.add_typer(diff.app, name="diff")
app.add_typer(serve.app, name="serve")

if __name__ == "__main__":
    app()
