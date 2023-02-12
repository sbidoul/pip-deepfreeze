import shlex
import sys
from typing import TYPE_CHECKING, Iterable, NewType

__all__ = ["shlex_join", "NormalizedName", "Protocol", "TypedDict"]

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


# https://github.com/pypa/packaging/pull/329
if TYPE_CHECKING:
    from packaging.utils import NormalizedName
else:
    NormalizedName = NewType("NormalizedName", str)
