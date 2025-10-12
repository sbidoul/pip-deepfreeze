import re
from collections.abc import Iterable

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import NormalizedName, canonicalize_name

# normalization regex from https://www.python.org/dev/peps/pep-0503/
_canonicalize_regex = re.compile(r"[-_.]+")
# regex adapted from https://packaging.python.org/specifications/core-metadata/#name
_egg_name_regex = re.compile(
    r"egg=([A-Z0-9][A-Z0-9._-]*[A-Z0-9]|[A-Z0-9])([^A-Z0-9._-]|$)", re.I
)


def _get_egg_name(requirement: str) -> str | None:
    mo = _egg_name_regex.search(requirement)
    if not mo:
        return None
    return mo.group(1)


def get_req_name(requirement: str) -> NormalizedName | None:
    name: str | None = None
    try:
        name = Requirement(requirement).name
    except InvalidRequirement:
        name = _get_egg_name(requirement)
    if not name:
        return None
    return canonicalize_name(name)


def get_req_names(requirements: Iterable[str]) -> list[NormalizedName]:
    req_names = []
    for requirement in requirements:
        req_name = get_req_name(requirement)
        if req_name:
            req_names.append(req_name)
    return req_names
