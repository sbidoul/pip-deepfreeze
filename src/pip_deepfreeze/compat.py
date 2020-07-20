import shlex
import sys
from typing import Iterable

__all__ = ["shlex_join", "resource_as_file", "resource_files", "Protocol"]

if sys.version_info >= (3, 8):
    from shlex import join as shlex_join
else:
    # compat
    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(s) for s in split_command)


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


if sys.version_info >= (3, 9):
    from importlib.resources import as_file as resource_as_file, files as resource_files
else:
    from importlib_resources import as_file as resource_as_file, files as resource_files
