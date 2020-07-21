from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .compat import shlex_join
from .list_depends import list_depends
from .project_name import get_project_name
from .req_file_parser import (
    NestedRequirementsLine,
    RequirementLine,
    parse as parse_req_file,
)
from .req_parser import get_req_name
from .utils import check_call, check_output, log_debug, log_info


def pip_upgrade_project(
    python: str,
    constraints_filename: Path,
    project_root: Path,
    extras: Optional[Iterable[str]] = None,
    editable: bool = True,
) -> None:
    """Upgrade a project.

    Make sure a project is installed with all its dependencies, and that all
    dependencies are at the latest version allowed by constraints.

    Ideally, this should be a native pip feature but
    - pip has difficulties upgrading direct URL requirements
      https://github.com/pypa/pip/issues/5780, https://github.com/pypa/pip/issues/7678
      (need to check if the new resolver does the exepected thing).
    - We need to pass --upgrade for regular requirements otherwise pip will not attempt
      to install them (requirement already satisfied).
    - Passing --upgrade to pip makes it too slow to my taste (need to check performance
      with the new resolver).

    In the meantime, here is our upgrade algorithm:
    1. List installed dependencies of project (pip_freeze_dependencies).
    2. Dependencies that are installed with a different version, or are not in
       constraints are uninstalled, to make sure they will be reinstalled according to
       the provided constraints or to the latest available version.
    3. Install project.

    This means one can upgrade a dependency by removing it from requirements.txt or
    update the version specifier in requirements.txt, and reinstalling the project with
    this function.
    """
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
        for req_line in pip_freeze_dependencies(python, project_root, extras)[0]
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
        to_uninstall_str = ",".join(to_uninstall)
        log_info(f"Uninstalling dependencies to update: {to_uninstall_str}")
        pip_uninstall(python, to_uninstall)
    # 4. install project with constraints
    # TODO Using -c here would break with the new pip resolver:
    #      https://github.com/pypa/pip/issues/8253 and in some other
    #      situations with the legacy resolver.
    #      If we can't make pip handle direct URLs as constraints,
    #      then the second best approach is to use -r here, and let
    #      sync's --uninstall option remove what we don't need.
    #      But the REQUESTED metadata will be incorrect.
    project_name = get_project_name(python, project_root)
    log_info(f"Installing/updating {project_name}")
    cmd = [python, "-m", "pip", "install", "-r", f"{constraints_filename}"]
    if editable:
        cmd.append("-e")
    if extras:
        extras_str = ",".join(extras)
        cmd.append(f"{project_root}[{extras_str}]")
    else:
        cmd.append(f"{project_root}")
    log_debug(f"Running {shlex_join(cmd)}")
    with open(constraints_filename) as f:
        constraints = f.read().strip()
        if constraints:
            log_debug(f"with {constraints_filename}:")
            log_debug(constraints)
        else:
            log_debug(f"with empty {constraints_filename}.")
    check_call(cmd)


def pip_freeze(python: str) -> Iterable[str]:
    """Run pip freeze."""
    cmd = [python, "-m", "pip", "freeze"]
    return check_output(cmd).splitlines()


def pip_freeze_dependencies(
    python: str, project_root: Path, extras: Optional[Iterable[str]] = None
) -> Tuple[List[str], List[str]]:
    """Run pip freeze, returning only dependencies of the project.

    Return the list of dependencies, and the list of other dependencies
    (except the project itself). Dependencies are returned in pip freeze
    format. Unnamed requirements are ignored.
    """
    project_name = get_project_name(python, project_root)
    if extras:
        raise NotImplementedError("extras")
    dependencies_names = list_depends(python, project_name)
    frozen_reqs = pip_freeze(python)
    dependencies_reqs = []
    unneeded_reqs = []
    for frozen_req in frozen_reqs:
        frozen_req_name = get_req_name(frozen_req)
        if not frozen_req_name:
            continue
        if frozen_req_name in dependencies_names:
            dependencies_reqs.append(frozen_req)
        elif frozen_req_name != project_name:
            unneeded_reqs.append(frozen_req)
    return dependencies_reqs, unneeded_reqs


def pip_uninstall(python: str, requirements: Iterable[str]) -> None:
    """Uninstall packages."""
    if list(requirements):
        cmd = [python, "-m", "pip", "uninstall", "--yes"] + list(requirements)
        check_call(cmd)
