from pathlib import Path
from typing import Iterable, Iterator, Optional

from packaging.utils import canonicalize_name

from .req_file_parser import OptionsLine, ParsedLine, RequirementLine, parse
from .req_parser import get_req_name
from .utils import HttpFetcher, log_error


def prepare_frozen_reqs_for_upgrade(
    frozen_requirements_paths: Iterable[Path],
    constraints_path: Path,
    upgrade_all: bool = False,
    to_upgrade: Optional[Iterable[str]] = None,
) -> Iterator[ParsedLine]:
    """Merge frozen requirements and constraints.

    pip options are taken from the constraints file. All frozen
    requirements are preserved, unless an upgrade is explicitly
    requested via ``upgrade_all`` or ``to_upgrade``. Other constraints
    not in frozen requirements are added.

    Yield tuples of (req_line, is_option).
    """
    to_upgrade_set = {canonicalize_name(r) for r in to_upgrade or []}
    constraints_reqs = []
    frozen_reqs_names = set()
    # 1. emit options from constraints_path, collect in_reqs
    if constraints_path.is_file():
        for constraint_req in parse(
            str(constraints_path),
            recurse=True,
            reqs_only=False,
            strict=True,
            http_fetcher=HttpFetcher(),
        ):
            if isinstance(constraint_req, OptionsLine):
                yield constraint_req
            elif isinstance(constraint_req, RequirementLine):
                constraint_req_name = get_req_name(constraint_req.requirement)
                if not constraint_req_name:
                    log_error(
                        f"Ignoring unnamed constraint {constraint_req.raw_line!r}."
                    )
                    continue
                constraints_reqs.append((constraint_req_name, constraint_req))
    # 2. emit existing frozen requirements unless upgrade_all or it is in to_upgrade
    for frozen_requirements_path in frozen_requirements_paths:
        if frozen_requirements_path.is_file() and not upgrade_all:
            for frozen_req in parse(
                str(frozen_requirements_path), recurse=True, reqs_only=True, strict=True
            ):
                assert isinstance(frozen_req, RequirementLine)
                constraint_req_name = get_req_name(frozen_req.requirement)
                if not constraint_req_name:
                    log_error(
                        f"Ignoring unnamed frozen requirement {frozen_req.raw_line!r}."
                    )
                    continue
                if constraint_req_name in to_upgrade_set:
                    continue
                frozen_reqs_names.add(constraint_req_name)
                yield frozen_req
    # 3. emit constraints requirements that have not been emitted as frozen reqs
    for constraint_req_name, constraint_req in constraints_reqs:
        if constraint_req_name not in frozen_reqs_names:
            yield constraint_req
