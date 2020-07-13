import shutil
from typing import List

import typer

from .sync import sync as sync_operation

app = typer.Typer()


class MainOptions:
    python: str


@app.command()
def sync(
    ctx: typer.Context,
    to_upgrade: List[str] = typer.Option(
        None,
        "--upgrade",
        "-u",
        metavar="DEPENDENCY",
        help=(
            "Make sure DEPENDENCY is upgraded (or downgraded) to the latest "
            "allowed version. If DEPENDENCY is not part of your application "
            "dependencies anymore, this option has no effect. "
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
    extras: List[str] = typer.Option(
        None,
        "-e",
        "--extra",
        metavar="EXTRA",
        help=("Extra to install. This option can be repeated."),
    ),
    editable: bool = typer.Option(True, help="Install the project in editable mode.",),
    uninstall: bool = typer.Option(
        False, help=("Uninstall dependencies that are not needed anymore.")
    ),
) -> None:
    sync_operation(ctx.obj.python, upgrade_all, to_upgrade, editable, extras, uninstall)


@app.callback()
def callback(
    ctx: typer.Context,
    python: str = typer.Option(default="python", show_default=True, metavar="PYTHON"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """
    A better pip freeze workflow for Python application developers.
    """
    python_abspath = shutil.which(python)
    # TODO error if not python_abspath
    ctx.obj.python = python_abspath
    # TODO prompt if python is same as sys.executable


def main() -> None:
    app(obj=MainOptions())


if __name__ == "__main__":
    main()
