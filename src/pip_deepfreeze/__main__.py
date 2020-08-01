import shutil
from pathlib import Path
from typing import Optional

import typer

from .detect import supports_editable
from .sync import sync as sync_operation
from .tree import tree as tree_operation
from .utils import comma_split, increase_verbosity, log_debug, log_error

app = typer.Typer()


class MainOptions:
    python: str
    project_root: Path


@app.command()
def sync(
    ctx: typer.Context,
    to_upgrade: str = typer.Option(
        None,
        "--update",
        "-u",
        metavar="DEP1,DEP2,...",
        help=(
            "Make sure selected dependencies are upgraded (or downgraded) to "
            "the latest allowed version. If DEP is not part of your application "
            "dependencies anymore, this option has no effect."
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
    # extras: str = typer.Option(
    #     None,
    #     "--extra",
    #     "-e",
    #     metavar="EXTRA",
    #     help="Extras to install.",
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
            "Uninstall distributions that are not dependencies of the project. "
            "If not specified, ask confirmation."
        ),
    ),
    use_pip_constraints: bool = typer.Option(
        True,
        help=(
            "Use pip --constraints instead of --requirements when passing "
            "pinned dependencies and constraints to pip. This has advantages "
            "such as marking only the project as REQUESTED, but may fail in "
            "some circumstances such as when using direct URLs with the new "
            "pip resolver."
        ),
    ),
) -> None:
    """Install/update the environment to match the project requirements.

    Install/reinstall the project. Install/update dependencies to the
    latest allowed version according to pinned dependencies in
    requirements.txt or constraints in requirements.txt.in. On demand
    update of dependencies to to the latest version that matches
    constraints. Optionally uninstall unneeded dependencies.
    """
    if editable is None:
        editable = supports_editable()
    elif editable and not supports_editable():
        log_error("The project does not support editable installation.",)
        raise typer.Exit(1)
    sync_operation(
        ctx.obj.python,
        upgrade_all,
        comma_split(to_upgrade),
        editable,
        extras=[],
        uninstall_unneeded=uninstall_unneeded,
        project_root=ctx.obj.project_root,
        use_pip_constraints=use_pip_constraints,
    )


@app.command()
def tree(
    ctx: typer.Context,
    extras: str = typer.Option(
        None,
        "--extras",
        "-e",
        metavar="EXTRAS",
        help="Extras of project to consider when looking for depdencies.",
    ),
) -> None:
    """Print the installed dependencies of the project as a tree."""
    tree_operation(
        ctx.obj.python, project_root=ctx.obj.project_root, extras=comma_split(extras)
    )


@app.callback()
def callback(
    ctx: typer.Context,
    python: str = typer.Option(
        "python",
        "--python",
        "-p",
        show_default=False,
        metavar="PYTHON",
        help=(
            "The python executable to use. Determines the python environment to "
            "work on. Defaults to the 'python' executable found in PATH."
        ),
    ),
    project_root: Path = typer.Option(
        ".",
        "--project-root",
        "-r",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        help="The project root directory.",
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
    # project directory
    ctx.obj.project_root = project_root
    log_debug(f"Looking for project in {project_root!r}")


def main() -> None:
    app(obj=MainOptions())


if __name__ == "__main__":
    main()
