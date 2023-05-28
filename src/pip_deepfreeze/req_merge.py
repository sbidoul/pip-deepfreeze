from pathlib import Path
from typing import Iterable, Iterator, Optional

from packaging.utils import canonicalize_name
from pip_requirements_parser import RequirementsFile  # type: ignore[import]

from .utils import log_error


def prepare_frozen_reqs_for_upgrade(
    frozen_filenames: Iterable[Path],
    in_filename: Path,
    upgrade_all: bool = False,
    to_upgrade: Optional[Iterable[str]] = None,
) -> Iterator[str]:
    """Merge frozen requirements and constraints.

    pip options are taken from the constraints file. All frozen
    requirements are preserved, unless an upgrade is explicitly
    requested via ``upgrade_all`` or ``to_upgrade``. Other constraints
    not in frozen requirements are added.
    """
    to_upgrade_set = {canonicalize_name(r) for r in to_upgrade or []}
    in_reqs = []
    frozen_reqs = set()
    # 1. emit options from in_filename, collect in_reqs
    if in_filename.is_file():
        in_req_file = RequirementsFile.from_file(str(in_filename), include_nested=True)
        for in_req_option in in_req_file.options:
            yield in_req_option.requirement_line.line
        for in_req in in_req_file.requirements:
            req_name = in_req.name
            if not req_name:
                log_error(
                    f"Ignoring unnamed constraint {in_req.requirement_line.line!r}."
                )
                continue
            in_reqs.append((req_name, in_req.requirement_line.line))
    # 2. emit frozen_reqs unless upgrade_all or it is in to_upgrade
    for frozen_filename in frozen_filenames:
        if frozen_filename.is_file() and not upgrade_all:
            for frozen_req in RequirementsFile.from_file(
                str(frozen_filename), include_nested=True
            ).requirements:
                req_name = frozen_req.name
                if not req_name:
                    log_error(
                        f"Ignoring unnamed frozen requirement "
                        f"{frozen_req.requirement_line.line!r}."
                    )
                    continue
                if req_name in to_upgrade_set:
                    continue
                frozen_reqs.add(req_name)
                yield frozen_req.requirement_line.line
    # 3. emit in_reqs that have not been emitted as frozen reqs
    for req_name, in_req_str in in_reqs:
        if req_name not in frozen_reqs:
            yield in_req_str
