from pathlib import Path
import shutil
import tempfile
from typing import List

import typer

from .pip import pip_upgrade_project

from .req_merge import prepare_frozen_reqs_for_upgrade

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
    with tempfile.NamedTemporaryFile(
        dir=".", prefix="requirements.", suffix=".txt.df", mode="w", encoding="utf-8"
    ) as constraints:
        for req_line in prepare_frozen_reqs_for_upgrade(
            Path("requirements.txt"), upgrade_all, to_upgrade
        ):
            print(req_line, file=constraints)
        constraints.flush()
        pip_upgrade_project(
            ctx.obj.python, Path(constraints.name), editable=editable, extras=extras
        )
        if uninstall:
            raise NotImplementedError("--uninstall not implemented yet")
        # TODO freeze dependencies, + options


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
