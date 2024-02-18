from pathlib import Path
from typing import List, Optional, Sequence

import typer
from packaging.utils import NormalizedName

from .pip import (
    Installer,
    pip_fixup_vcs_direct_urls,
    pip_freeze_dependencies_by_extra,
    pip_uninstall,
    pip_upgrade_project,
)
from .project_name import get_project_name
from .req_file_parser import OptionsLine, parse as parse_req_file
from .req_merge import prepare_frozen_reqs_for_upgrade
from .req_parser import get_req_name, get_req_names
from .utils import (
    HttpFetcher,
    get_temp_path_in_dir,
    log_debug,
    log_info,
    make_project_name_with_extras,
    make_requirements_path,
    make_requirements_paths,
    normalize_req_line,
    open_with_rollback,
    run_commands,
)


def _req_line_sort_key(req_line: str) -> str:
    req_name = get_req_name(req_line)
    if req_name is None:
        return req_line
    return req_name


def sync(
    python: str,
    upgrade_all: bool,
    to_upgrade: List[str],
    extras: List[NormalizedName],
    uninstall_unneeded: Optional[bool],
    project_root: Path,
    post_sync_commands: Sequence[str] = (),
    installer: Installer = Installer.envpip,
) -> None:
    project_name = get_project_name(python, project_root)
    project_name_with_extras = make_project_name_with_extras(project_name, extras)
    requirements_in = project_root / "requirements.txt.in"
    # upgrade project and its dependencies, if needed
    constraints_path = get_temp_path_in_dir(
        dir=project_root, prefix="requirements.", suffix=".txt.df"
    )
    with constraints_path.open(mode="w", encoding="utf-8") as constraints:
        for req_line in prepare_frozen_reqs_for_upgrade(
            make_requirements_paths(project_root, extras),
            requirements_in,
            upgrade_all,
            to_upgrade,
        ):
            print(req_line, file=constraints)
    pip_upgrade_project(
        python,
        constraints_path,
        project_root,
        extras=extras,
        installer=installer,
    )
    # freeze dependencies
    frozen_reqs_by_extra, unneeded_reqs = pip_freeze_dependencies_by_extra(
        python, project_root, extras
    )
    for extra, frozen_reqs in frozen_reqs_by_extra.items():
        requirements_frozen_path = make_requirements_path(project_root, extra)
        with open_with_rollback(requirements_frozen_path) as f:
            print("# frozen requirements generated by pip-deepfreeze", file=f)
            # output pip options in main requirements only
            if not extra and requirements_in.exists():
                # XXX can we avoid this second parse of requirements.txt.in?
                for parsed_req_line in parse_req_file(
                    str(requirements_in),
                    reqs_only=False,
                    recurse=True,
                    strict=True,
                    http_fetcher=HttpFetcher(),
                ):
                    if isinstance(parsed_req_line, OptionsLine):
                        print(parsed_req_line.raw_line, file=f)
            # output frozen dependencies of project,
            # sorted by canonical requirement name
            for req_line in sorted(frozen_reqs, key=_req_line_sort_key):
                print(normalize_req_line(req_line), file=f)
    # uninstall unneeded dependencies, if asked to do so
    unneeded_req_names = sorted(
        set(str(s) for s in get_req_names(unneeded_reqs))
        - set(["pip", "setuptools", "wheel", "distribute"])
    )
    if unneeded_req_names:
        unneeded_reqs_str = ",".join(unneeded_req_names)
        prompted = False
        if uninstall_unneeded is None:
            uninstall_unneeded = typer.confirm(
                typer.style(
                    f"The following distributions "
                    f"that are not dependencies of {project_name_with_extras} "
                    f"are also installed: {unneeded_reqs_str}.\n"
                    f"Do you want to uninstall them?",
                    bold=True,
                ),
                default=False,
                show_default=True,
            )
            prompted = True
        if uninstall_unneeded:
            log_info(f"Uninstalling unneeded distributions: {unneeded_reqs_str}")
            pip_uninstall(python, unneeded_req_names)
        elif not prompted:
            log_debug(
                f"The following distributions "
                f"that are not dependencies of {project_name_with_extras} "
                f"are also installed: {unneeded_reqs_str}"
            )
    # fixup VCS direct_url.json (see fixup-vcs-direct-urls.py for details on why)
    pip_fixup_vcs_direct_urls(python)
    # run post-sync commands
    run_commands(post_sync_commands, project_root, "post-sync")
