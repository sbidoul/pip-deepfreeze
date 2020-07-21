import re
from typing import Iterable, Iterator, Optional

from packaging.requirements import InvalidRequirement, Requirement

# normalization regex from https://www.python.org/dev/peps/pep-0503/
_canonicalize_regex = re.compile(r"[-_.]+")
# regex adapted from https://packaging.python.org/specifications/core-metadata/#name
_egg_name_regex = re.compile(
    r"egg=([A-Z0-9][A-Z0-9._-]*[A-Z0-9]|[A-Z0-9])([^A-Z0-9._-]|$)", re.I
)


def canonicalize_name(name: str) -> str:
    return _canonicalize_regex.sub("-", name).lower()


def _get_egg_name(requirement: str) -> Optional[str]:
    mo = _egg_name_regex.search(requirement)
    if not mo:
        return None
    return mo.group(1)


def get_req_name(requirement: str) -> Optional[str]:
    try:
        name = Requirement(requirement).name
    except InvalidRequirement:
        name = _get_egg_name(requirement)
    if not name:
        return None
    return canonicalize_name(name)


def get_req_names(requirements: Iterable[str]) -> Iterator[str]:
    for requirement in requirements:
        req_name = get_req_name(requirement)
        if req_name:
            yield req_name
