import json
import shlex
from importlib.resources import path as resource_path
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, TypedDict, cast

from packaging.utils import NormalizedName
from packaging.version import Version

from .installed_dist import (
    EnvInfoInstalledDistribution,
    InstalledDistributions,
    PipInspectInstalledDistribution,
)
from .list_installed_depends import (
    list_installed_depends,
    list_installed_depends_by_extra,
)
from .project_name import get_project_name
from .req_file_parser import (
    NestedRequirementsLine,
    RequirementLine,
    parse as parse_req_file,
)
from .req_parser import get_req_name
from .sanity import _get_env_info, get_pip_version
from .utils import (
    check_call,
    check_output,
    get_temp_path_in_dir,
    log_debug,
    log_info,
    log_warning,
    normalize_req_line,
)


class PipInspectReport(TypedDict, total=False):
    version: str
    installed: List[Dict[str, Any]]
    environment: Dict[str, str]


def pip_upgrade_project(
    python: str,
    constraints_filename: Path,
    project_root: Path,
    extras: Optional[Sequence[NormalizedName]] = None,
) -> None:
    """Upgrade a project.

    Make sure a project is installed with all its dependencies, and that all
    dependencies are at the latest version allowed by constraints.

    Ideally, this should be a native pip feature but
    - pip has difficulties upgrading direct URL requirements
      https://github.com/pypa/pip/issues/5780, https://github.com/pypa/pip/issues/7678
      (need to check if the new resolver does the expected thing).
    - We need to pass --upgrade for regular requirements otherwise pip will not attempt
      to install them (requirement already satisfied).
    - Passing --upgrade to pip makes it too slow to my taste (need to check performance
      with the new resolver).
    - pip does not support editable contraints

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
    constraints_without_editables_filename = get_temp_path_in_dir(
        dir=project_root, prefix="requirements.", suffix=".txt.df"
    )
    editable_constraints = []
    constraint_reqs = {}
    # 1. parse constraints, filter out editable constraints that pip does not support
    with constraints_without_editables_filename.open(
        mode="w", encoding="utf-8"
    ) as constraints_without_editables_file:
        for req_line in parse_req_file(
            str(constraints_filename), recurse=False, reqs_only=False
        ):
            assert not isinstance(req_line, NestedRequirementsLine)
            if isinstance(req_line, RequirementLine):
                req_name = get_req_name(req_line.requirement)
                assert req_name  # XXX user error instead?
                constraint_reqs[req_name] = normalize_req_line(req_line.requirement)
                if not req_line.is_editable:
                    print(req_line.raw_line, file=constraints_without_editables_file)
                else:
                    editable_constraints.extend(["-e", req_line.requirement])
            else:
                print(req_line.raw_line, file=constraints_without_editables_file)
    # 2. get installed frozen dependencies of project
    installed_reqs = {
        get_req_name(req_line): normalize_req_line(req_line)
        for req_line in pip_freeze_dependencies(python, project_root, extras)[0]
    }
    assert all(installed_reqs.keys())  # XXX user error instead?
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
    project_name = get_project_name(python, project_root)
    log_info(f"Installing/updating {project_name}")
    cmd = [
        python,
        "-m",
        "pip",
        "install",
        "-c",
        f"{constraints_without_editables_filename}",
        *editable_constraints,
    ]
    cmd.append("-e")
    if extras:
        extras_str = ",".join(extras)
        cmd.append(f"{project_root}[{extras_str}]")
    else:
        cmd.append(f"{project_root}")
    log_debug(f"Running {shlex.join(cmd)}")
    constraints = constraints_without_editables_filename.read_text(
        encoding="utf-8"
    ).strip()
    if constraints:
        log_debug(f"with {constraints_without_editables_filename}:")
        log_debug(constraints)
    else:
        log_debug(f"with empty {constraints_without_editables_filename}.")
    check_call(cmd)


def _pip_list__env_info_json(python: str) -> InstalledDistributions:
    with resource_path("pip_deepfreeze", "pip-list-json.py") as pip_list_json:
        json_dists = json.loads(check_output([python, str(pip_list_json)]))
        dists = [EnvInfoInstalledDistribution(json_dist) for json_dist in json_dists]
        return {dist.name: dist for dist in dists}


def _pip_inspect(python: str) -> PipInspectReport:
    return cast(
        PipInspectReport,
        json.loads(check_output([python, "-m", "pip", "--quiet", "inspect"])),
    )


def _pip_list__pip_inspect(python: str) -> InstalledDistributions:
    inspect = _pip_inspect(python)
    if inspect["version"] not in ("0", "1"):
        raise SystemExit(
            f"Unspported 'pip inspect' output format version '{inspect['version']}'"
        )
    environment = inspect["environment"]
    dists = [
        PipInspectInstalledDistribution(json_dist, environment)
        for json_dist in inspect["installed"]
    ]
    return {dist.name: dist for dist in dists}


def pip_list(python: str) -> InstalledDistributions:
    """List installed distributions."""
    if get_pip_version(python) >= Version("22.2"):
        return _pip_list__pip_inspect(python)
    else:
        return _pip_list__env_info_json(python)


def pip_freeze(python: str) -> Iterable[str]:
    """Run pip freeze."""
    cmd = [python, "-m", "pip", "freeze", "--all"]
    return check_output(cmd).splitlines()


def pip_freeze_dependencies(
    python: str, project_root: Path, extras: Optional[Sequence[NormalizedName]] = None
) -> Tuple[List[str], List[str]]:
    """Run pip freeze, returning only dependencies of the project.

    Return the list of installed direct and indirect dependencies of the
    project, and the list of other installed dependencies that are not
    dependencies of the project (except the project itself).
    Dependencies are returned in pip freeze format. Unnamed requirements
    are ignored.
    """
    project_name = get_project_name(python, project_root)
    dependencies_names = list_installed_depends(pip_list(python), project_name, extras)
    frozen_reqs = pip_freeze(python)
    dependencies_reqs = []
    unneeded_reqs = []
    for frozen_req in frozen_reqs:
        frozen_req_name = get_req_name(frozen_req)
        if not frozen_req_name:
            continue
        if frozen_req_name == project_name:
            continue
        if frozen_req_name in dependencies_names:
            dependencies_reqs.append(frozen_req)
        else:
            unneeded_reqs.append(frozen_req)
    return dependencies_reqs, unneeded_reqs


def pip_freeze_dependencies_by_extra(
    python: str, project_root: Path, extras: Sequence[NormalizedName]
) -> Tuple[Dict[Optional[NormalizedName], List[str]], List[str]]:
    """Run pip freeze, returning only dependencies of the project.

    Return the list of installed direct and indirect dependencies of the
    project grouped by extra, and the list of other installed
    dependencies that are not dependencies of the project (except the
    project itself). Dependencies are returned in pip freeze format.
    Unnamed requirements are ignored.
    """
    project_name = get_project_name(python, project_root)
    dependencies_by_extras = list_installed_depends_by_extra(
        pip_list(python), project_name
    )
    frozen_reqs = pip_freeze(python)
    dependencies_reqs = {}  # type: Dict[Optional[NormalizedName], List[str]]
    for extra in extras:
        if extra not in dependencies_by_extras:
            log_warning(f"{extra} is not an extra of {project_name}")
            continue
        dependencies_reqs[extra] = []
    dependencies_reqs[None] = []
    unneeded_reqs = []
    for frozen_req in frozen_reqs:
        frozen_req_name = get_req_name(frozen_req)
        if not frozen_req_name:
            continue
        if frozen_req_name == project_name:
            continue
        unneeded = True
        if frozen_req_name in dependencies_by_extras[None]:
            unneeded = False
            dependencies_reqs[None].append(frozen_req)
        else:
            for extra in extras:
                if frozen_req_name in dependencies_by_extras.get(extra, []):
                    unneeded = False
                    dependencies_reqs[extra].append(frozen_req)
        if unneeded:
            unneeded_reqs.append(frozen_req)
    return dependencies_reqs, unneeded_reqs


def pip_uninstall(python: str, requirements: Iterable[str]) -> None:
    """Uninstall packages."""
    reqs = list(requirements)
    if not reqs:
        return
    cmd = [python, "-m", "pip", "uninstall", "--yes", *reqs]
    check_call(cmd)


def pip_fixup_vcs_direct_urls(python: str) -> None:
    if Version(_get_env_info(python)["python_version"]) < Version("3.6"):
        # Not supported, and not needed with pip's legacy resolver.
        return
    # This will become unnecessary when pip caches metadata or
    # caches wheels that are built from a git ref that is not a commit
    # (it could cache it under a modified link where the git ref is replaced
    # by the commit id).
    with resource_path(
        "pip_deepfreeze", "fixup-vcs-direct-urls.py"
    ) as fixup_vcs_direct_urls:
        check_call([python, fixup_vcs_direct_urls])
