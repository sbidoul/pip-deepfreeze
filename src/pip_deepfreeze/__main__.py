import importlib.metadata
import shutil
from pathlib import Path
from typing import Annotated, Any

import typer
from packaging.utils import canonicalize_name
from packaging.version import Version

from .pip import Installer, InstallerFlavor
from .pyproject_toml import load_pyproject_toml
from .sanity import check_env
from .sync import sync as sync_operation
from .tree import tree as tree_operation
from .utils import comma_split, increase_verbosity, log_debug, log_error, log_warning

app = typer.Typer()


class MainOptions:
    python: str
    project_root: Path


@app.command()
def sync(
    ctx: typer.Context,
    to_upgrade: Annotated[
        str | None,
        typer.Option(
            "--update",
            "-u",
            metavar="DEP1,DEP2,...",
            help=(
                "Make sure selected dependencies are upgraded (or downgraded) to "
                "the latest allowed version. If DEP is not part of your application "
                "dependencies anymore, this option has no effect."
            ),
        ),
    ] = None,
    upgrade_all: Annotated[
        bool,
        typer.Option(
            "--update-all",
            help=(
                "Upgrade (or downgrade) all dependencies of your application to "
                "the latest allowed version."
            ),
            show_default=False,
        ),
    ] = False,
    extras: Annotated[
        str | None,
        typer.Option(
            "--extras",
            "-x",
            metavar="EXTRA1,EXTRA2,...",
            help=(
                "Comma separated list of extras "
                "to install and freeze to requirements-{EXTRA}.txt."
            ),
        ),
    ] = None,
    uninstall_unneeded: Annotated[
        bool | None,
        typer.Option(
            help=(
                "Uninstall distributions that are not dependencies of the project. "
                "If not specified, ask confirmation."
            ),
        ),
    ] = None,
    pre_sync_commands: Annotated[
        list[str] | None,
        typer.Option(
            "--pre-sync-command",
            help=(
                "Command to run before the sync operation. "
                "Can be specified multiple times."
            ),
        ),
    ] = None,
    post_sync_commands: Annotated[
        list[str] | None,
        typer.Option(
            "--post-sync-command",
            help=(
                "Command to run after the sync operation is complete. "
                "Can be specified multiple times."
            ),
        ),
    ] = None,
    installer: Annotated[
        InstallerFlavor,
        typer.Option(),
    ] = InstallerFlavor.pip,
    build_constraints: Annotated[
        Path | None,
        typer.Option(
            dir_okay=False,
            file_okay=True,
            exists=True,
        ),
    ] = None,
    build_contraints: Annotated[  # backward compatibility with a typo
        Path | None,
        typer.Option(
            dir_okay=False,
            file_okay=True,
            exists=True,
            hidden=True,
        ),
    ] = None,
) -> None:
    """Install/update the environment to match the project requirements.

    Install/reinstall the project. Install/update dependencies to the
    latest allowed version according to pinned dependencies in
    requirements.txt or constraints in constraints.txt/requirements.txt.in. On demand
    update of dependencies to to the latest version that matches
    constraints. Optionally uninstall unneeded dependencies.
    """
    if build_contraints:
        log_warning(
            "--build-contraints is deprecated, use --build-constraints instead."
        )
    sync_operation(
        Installer.create(flavor=installer, python=ctx.obj.python),
        ctx.obj.python,
        upgrade_all,
        comma_split(to_upgrade),
        extras=[canonicalize_name(extra) for extra in comma_split(extras)],
        uninstall_unneeded=uninstall_unneeded,
        project_root=ctx.obj.project_root,
        pre_sync_commands=pre_sync_commands or [],
        post_sync_commands=post_sync_commands or [],
        build_constraints=build_constraints or build_contraints,
    )


@app.command()
def tree(
    ctx: typer.Context,
    extras: Annotated[
        str | None,
        typer.Option(
            "--extras",
            "-x",
            metavar="EXTRA1,EXTRA2,...",
            help="Extras of project to consider when looking for dependencies.",
        ),
    ] = None,
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


def _find_python_from(pythons: list[str]) -> str:
    for python in pythons:
        python_abspath = shutil.which(python)
        if python_abspath:
            return python_abspath
    log_error(f"Python interpreter not found ({', '.join(pythons)}).")
    raise typer.Exit(1)


def _find_python(python: str | None) -> str:
    if python:
        return _find_python_from([python])
    return _find_python_from(["py", "python"])


def _version(value: Any) -> None:
    if value:
        version = importlib.metadata.version("pip-deepfreeze")
        typer.echo(f"pip-deepfreeze {version}")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    python: Annotated[
        str | None,
        typer.Option(
            "--python",
            "--py",
            "-p",
            show_default=False,
            metavar="PYTHON",
            help=(
                "The python executable to use. Determines the python environment to "
                "work on. Defaults to the 'py' or 'python' executable found in PATH."
            ),
        ),
    ] = None,
    project_root: Annotated[
        Path,
        typer.Option(
            "--project-root",
            "-r",
            # Process this parameter first so we can load default values from
            # pyproject.toml
            is_eager=True,
            callback=project_root_callback,
            exists=True,
            dir_okay=True,
            file_okay=False,
            resolve_path=True,
            help="The project root directory.",
        ),
    ] = Path("."),
    min_version: Annotated[
        str | None,
        typer.Option(
            "--min-version",
            metavar="VERSION",
            help="Minimum version of pip-deepfreeze required.",
        ),
    ] = None,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version,
            help="Show the version and exit.",
            is_eager=True,
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            show_default=False,
        ),
    ] = False,
) -> None:
    """A simple pip freeze workflow for Python application developers."""
    if min_version:
        current_version = importlib.metadata.version("pip-deepfreeze")
        if Version(current_version) < Version(min_version):
            log_error(
                f"pip-deepfreeze {min_version} or later is required. "
                f"Current version is {current_version}."
            )
            raise typer.Exit(1)
    # handle verbosity/quietness
    if verbose:
        increase_verbosity()
    # find python
    ctx.obj.python = _find_python(python)
    log_debug(f"Using python {ctx.obj.python}")
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
