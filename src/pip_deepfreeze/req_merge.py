from pathlib import Path
import shlex
from typing import Dict, Iterable, Iterator, Optional

try:
    from shlex import join as shlex_join
except ImportError:
    # python < 3.8
    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(s) for s in split_command)


import httpx

from .req_file_parser import parse, RequirementLine, OptionsLine
from .req_parser import canonicalize_name, get_req_name


def prepare_frozen_reqs_for_upgrade(
    frozen_filename: Path,
    upgrade_all: bool = False,
    to_upgrade: Optional[Iterable[str]] = None,
) -> Iterator[str]:
    to_upgrade_set = {canonicalize_name(r) for r in to_upgrade or []}
    in_reqs: Dict[str, str] = {}
    frozen_reqs: Dict[str, str] = {}
    # 1. emit options from in_filename, collect in_reqs
    in_filename = frozen_filename.with_name(frozen_filename.name + ".in")
    if in_filename.is_file():
        for in_req in parse(
            str(in_filename),
            recurse=True,
            reqs_only=False,
            strict=True,
            session=httpx.Client(),
        ):
            if isinstance(in_req, OptionsLine):
                yield shlex_join(in_req.options)
            elif isinstance(in_req, RequirementLine):
                req_name = get_req_name(in_req.requirement)
                if not req_name:
                    # TODO warn or error
                    continue
                in_reqs[req_name] = in_req.requirement
    # 2. emit frozen_reqs unless upgrade_all or it is in to_upgrade
    if frozen_filename.is_file():
        for frozen_req in parse(
            str(frozen_filename), recurse=True, reqs_only=True, strict=True
        ):
            assert isinstance(frozen_req, RequirementLine)
            req_name = get_req_name(frozen_req.requirement)
            if not req_name:
                # TODO warn or error
                continue
            if upgrade_all or req_name in to_upgrade_set:
                continue
            frozen_reqs[req_name] = frozen_req.requirement
            yield frozen_req.requirement
    # 3. emit in_reqs that have not been emitted as frozen reqs
    for req_name in in_reqs:
        if req_name not in frozen_reqs:
            yield in_reqs[req_name]
