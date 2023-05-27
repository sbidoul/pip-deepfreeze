import shlex
import sys
from typing import Iterable

__all__ = ["shlex_join", "tomllib", "Protocol", "TypedDict"]

if sys.version_info >= (3, 8):
    from shlex import join as shlex_join
else:
    # compat
    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(s) for s in split_command)


if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict
else:
    from typing_extensions import Protocol, TypedDict


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
