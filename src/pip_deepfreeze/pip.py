from pathlib import Path
import subprocess
from typing import Iterable, Optional


def pip_upgrade_project(
    python: str,
    requirements_filename: Path,
    project_root: Path = Path("."),
    extras: Optional[Iterable[str]] = None,
    editable: bool = True,
) -> None:
    # Ideally, this should be a native pip feature but
    # - pip has difficulties upgrading direct URL requirements
    #   https://github.com/pypa/pip/issues/5780
    #   https://github.com/pypa/pip/issues/7678
    #   (need to check if the new resolver does the right thing).
    # - we need to pass --upgrade for regular requirements otherwise
    #   pip will not attempt to install them (requirement already satisfied)
    # - passing --upgrade to pip makes it very slow
    # TODO smart upgrade algorithm
    #      - list installed dependencies of project (pip_freeze_dependencies)
    #      - dependencies that are different or not in requirements_filename
    #        must be uninstalled
    #      - then install project
    cmd = [python, "-m", "pip", "install", "-r", requirements_filename]
    if editable:
        cmd.append("-e")
    if extras:
        extras_str = ",".join(extras)
        cmd.append(str(project_root) + f"[{extras_str}]")
    else:
        cmd.append(str(project_root))
    subprocess.check_call(cmd)  # type: ignore


def pip_freeze(python: str) -> Iterable[str]:
    cmd = [python, "-m", "pip", "freeze"]
    frozen = subprocess.check_output(cmd, universal_newlines=True).strip()
    if not frozen:
        return []
    return frozen.split("\n")


def pip_freeze_dependencies(
    python: str, project_root: Path = Path("."), extras: Optional[Iterable[str]] = None
) -> Iterable[str]:
    ...


def pip_uninstall(python: str, requirements: Iterable[str]) -> None:
    cmd = [python, "-m", "pip", "uninstall", "--yes"] + list(requirements)
    subprocess.check_call(cmd)
