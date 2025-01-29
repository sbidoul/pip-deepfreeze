from collections.abc import Sequence
from pathlib import Path
from typing import Optional

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
    make_frozen_requirements_path,
    make_frozen_requirements_paths,
    make_project_name_with_extras,
    normalize_req_line,
    open_with_rollback,
    run_commands,
)


def _req_line_sort_key(req_line: str) -> str:
    req_name = get_req_name(req_line)
    if req_name is None:
        return req_line
    return req_name


def _constraints_path(project_root: Path) -> Path:
    constraints_txt = project_root / "constraints.txt"
    if not constraints_txt.is_file():
        # fallback to requirements.txt.in if it exists, for backward compatibility
        requirements_txt_in = project_root / "requirements.txt.in"
        if requirements_txt_in.is_file():
            log_debug(
                "Reading constraints and pip options "
                "from 'requirements.txt.in'. "
                "Consider renaming it to 'constraints.txt' "
                "as this name better describes the purpose of the file."
            )
            return requirements_txt_in
    return constraints_txt


def sync(
    installer: Installer,
    python: str,
    upgrade_all: bool,
    to_upgrade: list[str],
    extras: list[NormalizedName],
    uninstall_unneeded: Optional[bool],
    project_root: Path,
    pre_sync_commands: Sequence[str] = (),
    post_sync_commands: Sequence[str] = (),
) -> None:
    # run pre-sync commands
    run_commands(pre_sync_commands, project_root, "pre-sync")
    # sync
    project_name = get_project_name(python, project_root)
    project_name_with_extras = make_project_name_with_extras(project_name, extras)
    constraints_path = _constraints_path(project_root)
    # upgrade project and its dependencies, if needed
    merged_constraints_path = get_temp_path_in_dir(
        dir=project_root, prefix="requirements.", suffix=".txt.df"
    )
    installer_options = []
    with merged_constraints_path.open(mode="w", encoding="utf-8") as constraints:
        for req_line in prepare_frozen_reqs_for_upgrade(
            make_frozen_requirements_paths(project_root, extras),
            constraints_path,
            upgrade_all,
            to_upgrade,
        ):
            if isinstance(req_line, OptionsLine):
                installer_options.extend(req_line.options)
            else:
                print(req_line.raw_line, file=constraints)
    pip_upgrade_project(
        installer,
        python,
        merged_constraints_path,
        project_root,
        extras=extras,
        installer_options=installer_options,
    )
    # freeze dependencies
    frozen_reqs_by_extra, unneeded_reqs = pip_freeze_dependencies_by_extra(
        installer, python, project_root, extras
    )
    for extra, frozen_reqs in frozen_reqs_by_extra.items():
        frozen_requirements_path = make_frozen_requirements_path(project_root, extra)
        with open_with_rollback(frozen_requirements_path) as f:
            print("# frozen requirements generated by pip-deepfreeze", file=f)
            # output pip options in main requirements only
            if not extra and constraints_path.exists():
                # XXX can we avoid this second parse of
                # constraints.txt/requirements.txt.in?
                for parsed_req_line in parse_req_file(
                    str(constraints_path),
                    reqs_only=False,
                    recurse=True,
                    strict=True,
                    http_fetcher=HttpFetcher(),
                ):
                    if isinstance(parsed_req_line, OptionsLine):
                        print(parsed_req_line.raw_line, file=f)
            # output frozen dependencies of project,
            # sorted by canonical requirement name
            for frozen_req in sorted(frozen_reqs, key=_req_line_sort_key):
                print(normalize_req_line(frozen_req), file=f)
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
            pip_uninstall(installer, python, unneeded_req_names)
        elif not prompted:
            log_debug(
                f"The following distributions "
                f"that are not dependencies of {project_name_with_extras} "
                f"are also installed: {unneeded_reqs_str}"
            )
    # fixup VCS direct_url.json (see fixup-vcs-direct-urls.py for details on why)
    if not installer.has_metadata_cache():
        pip_fixup_vcs_direct_urls(python)
    # run post-sync commands
    run_commands(post_sync_commands, project_root, "post-sync")
