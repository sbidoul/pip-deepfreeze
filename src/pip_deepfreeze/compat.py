import shlex
import sys
from typing import Iterable

if sys.version_info >= (3, 8):
    from shlex import join as shlex_join
else:
    # compat
    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(s) for s in split_command)
