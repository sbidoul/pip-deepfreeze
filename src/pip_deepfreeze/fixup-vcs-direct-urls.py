#!/usr/bin/env python

import json
import re
import sys
from pathlib import Path
from typing import List

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    try:
        import importlib_metadata  # type: ignore
    except ImportError:
        print(
            "Warning: not fixing up VCS URLs because nor "
            "importlib_metadata nor importlib.metadata are available. "
            "Please install importlib_metadata in the target environment "
            "or upgrade to Python 3.8+."
        )
        sys.exit(0)

_canonicalize_regex = re.compile(r"[-_.]+")


def _canonicalize_name(name: str) -> str:
    return _canonicalize_regex.sub("_", name).lower()


def fixup_vcs_direct_url(dist: importlib_metadata.Distribution) -> None:
    """Fixup VCS direct_url.json to set a fake commit_id when it is different from
    requested_revision.

    So a subsequent install of the same VCS URL with a commit-id instead of the
    tag/branch/ref will actually reinstall. Otherwise pip will clone and compute
    the metadata again, but will not build the package, and therefore never
    cache it.
    """
    canonical_name = _canonicalize_name(dist.metadata["Name"])
    direct_url_path = Path(
        dist.locate_file(f"{canonical_name}-{dist.version}.dist-info/direct_url.json")
    )
    if not direct_url_path.is_file():
        return
    try:
        direct_url = json.loads(direct_url_path.read_text(encoding="utf-8"))
    except Exception:
        return  # invalid direct_url.json
    vcs_info = direct_url.get("vcs_info")
    if not vcs_info:
        return  # not a VCS direct URL
    commit_id = vcs_info.get("commit_id")
    if not commit_id:
        return  # invalid direct_url.json
    if vcs_info.get("requested_revision") == commit_id:
        return  # nothing to do
    print("fixing up", direct_url_path)
    vcs_info["commit_id"] = "f" * 40  # fake commit_id
    direct_url_path.write_text(json.dumps(direct_url), encoding="utf-8")


def fixup_direct_urls(names: List[str]) -> None:
    for dist in importlib_metadata.distributions():
        fixup_vcs_direct_url(dist)


if __name__ == "__main__":
    fixup_direct_urls(sys.argv[1:])
