from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import List

import typer

from .req_merge import prepare_frozen_reqs_for_update

app = typer.Typer()


class MainOptions:
    python: str


@app.command()
def sync(
    ctx: typer.Context,
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
        help=("Extra to install. This option can be repeated."),
    ),
    editable: bool = typer.Option(True, help="Install the project in editable mode.",),
    uninstall: bool = typer.Option(
        False, help=("Uninstall dependencies that are not needed anymore.")
    ),
) -> None:
    with tempfile.NamedTemporaryFile(
        dir=".", prefix="requirements.df", suffix=".txt", mode="w", encoding="utf-8"
    ) as f:
        for req_line in prepare_frozen_reqs_for_update(
            Path("requirements.txt"), update_all=upgrade_all, to_update=upgrade
        ):
            print(req_line, file=f)
        f.flush()
        install_cmd = [ctx.obj.python, "-m", "pip", "install", "-r", f.name]
        if editable:
            install_cmd.append("-e")
        if extra:
            raise NotImplementedError()
            extra_str = ",".join(extra)
            install_cmd.append(f".[{extra_str}]")
        else:
            install_cmd.append(".")
        subprocess.check_call(install_cmd)
        if uninstall:
            raise NotImplementedError()


@app.command()
def freeze() -> None:
    ...


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
