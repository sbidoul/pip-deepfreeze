from typing import List

import typer

app = typer.Typer()


@app.command()
def sync(
    upgrade: List[str] = typer.Option(
        None,
        "--upgrade",
        "-u",
        metavar="DEPENDENCY",
        help=(
            "Make sure DEPENDENCY is upgraded to the latest allowed version. "
            "If DEPENDENCY is not part of your application dependencies "
            "anymore, this option has no effect. "
            "This option can be repeated."
        ),
    ),
    upgrade_all: bool = typer.Option(
        False,
        "--upgrade-all",
        help=(
            "Upgrade all dependencies of your application to "
            "the latest allowed version."
        ),
        show_default=False,
    ),
    extra: List[str] = typer.Option(
        None,
        "-e",
        "--extra",
        metavar="EXTRA",
        help=(
            "Extra to install. :all: can be used to install all extras "
            "provided by the application (note the colons). "
            "This option can be repeated."
        ),
    ),
    editable: bool = typer.Option(True, help="Install the project in editable mode.",),
    uninstall: bool = typer.Option(
        True, help=("Uninstall dependencies that are not needed anymore.")
    ),
):
    typer.echo(extra)
    typer.echo(upgrade)


@app.command()
def appfreeze():
    ...


@app.callback()
def callback(
    python: str = typer.Option(default="python", show_default=True, metavar="PYTHON"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """
    A better pip freeze workflow for Python application developers.
    """
    pass


if __name__ == "__main__":
    app()
