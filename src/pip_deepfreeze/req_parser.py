import re
from typing import Optional

from packaging.requirements import Requirement, InvalidRequirement


_canonicalize_regex = re.compile(r"[-_.]+")


def canonicalize_name(name: str) -> str:
    # This is taken from PEP 503.
    return _canonicalize_regex.sub("-", name).lower()


def get_req_name(requirement: str) -> Optional[str]:
    try:
        req = Requirement(requirement)
    except InvalidRequirement:
        return None
    else:
        return canonicalize_name(req.name)
