import tempfile
from pathlib import Path
from typing import List

import httpx

from .pip import pip_freeze_dependencies, pip_uninstall, pip_upgrade_project
from .project_name import get_project_name
from .req_file_parser import OptionsLine, parse as parse_req_file
from .req_merge import prepare_frozen_reqs_for_upgrade
from .req_parser import get_req_name
from .utils import log_debug, log_info, open_with_rollback


def sync(
    python: str,
    upgrade_all: bool,
    to_upgrade: List[str],
    editable: bool,
    extras: List[str],
    uninstall_unneeded: bool,
    project_root: Path,
) -> None:
    project_name = get_project_name(python, project_root)
    requirements_frozen = project_root / "requirements.txt"
    requirements_in = project_root / "requirements.txt.in"
    # upgrade project and its dependencies, if needed
    with tempfile.NamedTemporaryFile(
        dir=project_root,
        prefix="requirements.",
        suffix=".txt.df",
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as constraints:
        for req_line in prepare_frozen_reqs_for_upgrade(
            requirements_frozen, requirements_in, upgrade_all, to_upgrade
        ):
            print(req_line, file=constraints)
    constraints_path = Path(constraints.name)
    try:
        pip_upgrade_project(
            python, constraints_path, project_root, editable=editable, extras=extras,
        )
    finally:
        constraints_path.unlink()
    # freeze dependencies
    log_info(f"Updating {requirements_frozen}")
    frozen_reqs, unneeded_reqs = pip_freeze_dependencies(python, project_root, extras)
    with open_with_rollback(requirements_frozen) as f:
        print("# frozen requirements generated by pip-deepfreeze", file=f)
        # output pip options
        if requirements_in.exists():
            # TODO can we avoid this second parse of requirements.txt.in?
            for parsed_req_line in parse_req_file(
                str(requirements_in),
                reqs_only=False,
                recurse=True,
                strict=True,
                session=httpx.Client(),
            ):
                if isinstance(parsed_req_line, OptionsLine):
                    print(parsed_req_line.raw_line, file=f)
        # output frozen dependencies of project
        for req_line in frozen_reqs:
            print(req_line, file=f)
    # uninstall unneeded dependencies, if asked to do so
    if unneeded_reqs:
        unneeded_req_names = [get_req_name(r) for r in unneeded_reqs]
        unneeded_req_names2 = [n for n in unneeded_req_names if n]
        unneeded_reqs_str = ",".join(unneeded_req_names2)
        if uninstall_unneeded:
            log_info(f"Uninstalling unneeded distributions: {unneeded_reqs_str}")
            pip_uninstall(python, unneeded_req_names2)
        else:
            log_debug(
                f"The following distributions "
                f"that are not dependencies of {project_name} "
                f"are installed: {unneeded_reqs_str}"
            )
