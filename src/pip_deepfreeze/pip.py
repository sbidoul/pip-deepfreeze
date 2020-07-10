import subprocess
from pathlib import Path
from typing import Iterable, Optional

from .list_depends import list_depends
from .project_name import get_project_name
from .req_file_parser import (
    NestedRequirementsLine,
    RequirementLine,
    parse as parse_req_file,
)
from .req_parser import get_req_name
from .utils import split_lines


def pip_upgrade_project(
    python: str,
    constraints_filename: Path,
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
    # - passing --upgrade to pip makes it slow
    #
    # In the meantime, here is our upgrade algorithm
    # - list installed dependencies of project (pip_freeze_dependencies)
    # - dependencies that are different or not in constraints
    #   are uninstalled, to make sure they will be reinstalled according
    #   to the provided constraints or to the latest available version
    # - install project
    # With this mechanism, one can upgrade a dependency by removing
    # it from requirements.txt, and reinstalling the project with this
    # algorithm.
    if extras:
        raise NotImplementedError("extras not implemented")
    # 1. parse constraints
    constraint_reqs = {}
    for req_line in parse_req_file(
        str(constraints_filename), recurse=False, reqs_only=False
    ):
        assert not isinstance(req_line, NestedRequirementsLine)
        if isinstance(req_line, RequirementLine):
            req_name = get_req_name(req_line.requirement)
            assert req_name  # TODO user error instead?
            constraint_reqs[req_name] = req_line.requirement
    # 2. get installed frozen dependencies of project
    installed_reqs = {
        get_req_name(req_line): req_line
        for req_line in pip_freeze_dependencies(python, project_root)
    }
    assert all(installed_reqs.keys())  # TODO user error instead?
    # 3. uninstall dependencies that do not match constraints
    to_uninstall = set()
    for installed_req_name, installed_req in installed_reqs.items():
        assert installed_req_name
        if installed_req_name not in constraint_reqs:
            to_uninstall.add(installed_req_name)
        elif installed_req != constraint_reqs[installed_req_name]:
            to_uninstall.add(installed_req_name)
    if to_uninstall:
        pip_uninstall(python, to_uninstall)
    # 4. install project with constraints
    cmd = [python, "-m", "pip", "install", "-r", f"{constraints_filename}"]
    if editable:
        # TODO if not editblae, uninstall project
        cmd.append("-e")
    if extras:
        extras_str = ",".join(extras)
        cmd.append(f"{project_root}[{extras_str}]")
    else:
        cmd.append(f"{project_root}")
    subprocess.check_call(cmd)


def pip_freeze(python: str) -> Iterable[str]:
    cmd = [python, "-m", "pip", "freeze"]
    return split_lines(subprocess.check_output(cmd, universal_newlines=True))


def pip_freeze_dependencies(
    python: str, project_root: Path = Path("."), extras: Optional[Iterable[str]] = None
) -> Iterable[str]:
    project_name = get_project_name(project_root)
    dependencies = list_depends(python, project_name)
    frozen = pip_freeze(python)
    for frozen_req in frozen:
        frozen_req_name = get_req_name(frozen_req)
        if not frozen_req_name:
            continue
        if frozen_req_name in dependencies:
            yield frozen_req


def pip_uninstall(python: str, requirements: Iterable[str]) -> None:
    cmd = [python, "-m", "pip", "uninstall", "--yes"] + list(requirements)
    subprocess.check_call(cmd)
