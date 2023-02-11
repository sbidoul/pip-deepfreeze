import shutil
from pathlib import Path
from typing import Any, List

import typer
from packaging.utils import canonicalize_name

from .pyproject_toml import load_pyproject_toml
from .sanity import check_env
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
    extras: str = typer.Option(
        None,
        "--extras",
        "-x",
        metavar="EXTRAS",
        help=(
            "Comma separated list of extras "
            "to install and freeze to requirements-{EXTRA}.txt."
        ),
    ),
    uninstall_unneeded: bool = typer.Option(
        None,
        help=(
            "Uninstall distributions that are not dependencies of the project. "
            "If not specified, ask confirmation."
        ),
    ),
    post_sync_commands: List[str] = typer.Option(
        [],
        "--post-sync-command",
        help=(
            "Command to run after the sync operation is complete. "
            "Can be specified multiple times."
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
    sync_operation(
        ctx.obj.python,
        upgrade_all,
        comma_split(to_upgrade),
        extras=[canonicalize_name(extra) for extra in comma_split(extras)],
        uninstall_unneeded=uninstall_unneeded,
        project_root=ctx.obj.project_root,
        post_sync_commands=post_sync_commands,
    )


@app.command()
def tree(
    ctx: typer.Context,
    extras: str = typer.Option(
        None,
        "--extras",
        "-x",
        metavar="EXTRAS",
        help="Extras of project to consider when looking for dependencies.",
    ),
) -> None:
    """Print the installed dependencies of the project as a tree."""
    tree_operation(
        ctx.obj.python,
        project_root=ctx.obj.project_root,
        extras=[canonicalize_name(extra) for extra in comma_split(extras)],
    )


def project_root_callback(ctx: typer.Context, param: Any, value: Path) -> Path:
    pyproject_toml = load_pyproject_toml(value)
    if pyproject_toml:
        ctx.default_map = pyproject_toml.get("tool", {}).get("pip-deepfreeze", {})
    return value


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
        # Process this parameter first so we can load default values from pyproject.toml
        is_eager=True,
        callback=project_root_callback,
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
    log_debug(f"Using python {python_abspath}")
    # sanity checks
    if not check_env(ctx.obj.python):
        raise typer.Exit(1)
    # project directory
    ctx.obj.project_root = project_root
    log_debug(f"Looking for project in {project_root}")


def main() -> None:
    app(obj=MainOptions())


if __name__ == "__main__":
    main()
