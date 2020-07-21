import shutil
from pathlib import Path
from typing import List, Optional

import typer

from .detect import supports_editable
from .sync import sync as sync_operation
from .utils import increase_verbosity, log_debug, log_error

app = typer.Typer()


class MainOptions:
    python: str


@app.command()
def sync(
    ctx: typer.Context,
    to_upgrade: List[str] = typer.Option(
        None,
        "--update",
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
        "--update-all",
        help=(
            "Upgrade (or downgrade) all dependencies of your application to "
            "the latest allowed version."
        ),
        show_default=False,
    ),
    # extras: List[str] = typer.Option(
    #     None,
    #     "-e",
    #     "--extra",
    #     metavar="EXTRA",
    #     help=("Extra to install. This option can be repeated."),
    # ),
    editable: Optional[bool] = typer.Option(
        None,
        help=(
            "Install the project in editable mode. "
            "Defaults to editable if the project supports it."
        ),
        show_default=False,
    ),
    uninstall_unneeded: bool = typer.Option(
        None,
        help=(
            "Uninstall dependencies that are not needed anymore. "
            "If not specified, ask confirmation."
        ),
    ),
) -> None:
    if editable is None:
        editable = supports_editable()
    elif editable and not supports_editable():
        log_error("The project does not support editable installation.",)
        raise typer.Exit(1)
    sync_operation(
        ctx.obj.python,
        upgrade_all,
        to_upgrade,
        editable,
        extras=[],
        uninstall_unneeded=uninstall_unneeded,
        project_root=Path.cwd(),
    )


@app.callback()
def callback(
    ctx: typer.Context,
    python: str = typer.Option(
        default="python",
        show_default=False,
        metavar="PYTHON",
        help=(
            "The python executable to use. Determines the virtual environment into "
            "which the project is to be installed. Defaults to the 'python' executable "
            "found in PATH."
        ),
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", show_default=False),
) -> None:
    """A simple pip freeze workflow for Python application developers."""
    # handle verbosity/quietness
    if verbose:
        increase_verbosity()
    # find python
    python_abspath = shutil.which(python)
    if not python_abspath:
        log_error(f"Python interpreter {python!r} not found.")
        raise typer.Exit(1)
    ctx.obj.python = python_abspath
    log_debug(f"Using {python_abspath}")


def main() -> None:
    app(obj=MainOptions())


if __name__ == "__main__":
    main()
