import shlex
from pathlib import Path
from typing import Iterable, Iterator, Optional

from packaging.utils import canonicalize_name

from .req_file_parser import OptionsLine, RequirementLine, parse
from .req_parser import get_req_name
from .utils import HttpFetcher, log_error


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
        for in_req in parse(
            str(in_filename),
            recurse=True,
            reqs_only=False,
            strict=True,
            http_fetcher=HttpFetcher(),
        ):
            if isinstance(in_req, OptionsLine):
                yield shlex.join(in_req.options)
            elif isinstance(in_req, RequirementLine):
                req_name = get_req_name(in_req.requirement)
                if not req_name:
                    log_error(f"Ignoring unnamed constraint {in_req.raw_line!r}.")
                    continue
                in_reqs.append((req_name, in_req))
    # 2. emit frozen_reqs unless upgrade_all or it is in to_upgrade
    for frozen_filename in frozen_filenames:
        if frozen_filename.is_file() and not upgrade_all:
            for frozen_req in parse(
                str(frozen_filename), recurse=True, reqs_only=True, strict=True
            ):
                assert isinstance(frozen_req, RequirementLine)
                req_name = get_req_name(frozen_req.requirement)
                if not req_name:
                    log_error(
                        f"Ignoring unnamed frozen requirement {frozen_req.raw_line!r}."
                    )
                    continue
                if req_name in to_upgrade_set:
                    continue
                frozen_reqs.add(req_name)
                yield frozen_req.raw_line
    # 3. emit in_reqs that have not been emitted as frozen reqs
    for req_name, in_req in in_reqs:
        if req_name not in frozen_reqs:
            yield in_req.raw_line
