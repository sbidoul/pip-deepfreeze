import contextlib
import shlex
from pathlib import Path
from typing import IO, Any, Iterable, Iterator, List

try:
    from shlex import join as shlex_join
except ImportError:
    # python < 3.8
    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(s) for s in split_command)


def split_lines(s: str) -> List[str]:
    s = s.strip()
    if not s:
        return []
    return s.split("\n")


@contextlib.contextmanager
def open_with_rollback(
    filename: Path, mode: str = "w", suffix: str = ".tmp"
) -> Iterator[IO[Any]]:
    temp_filename = filename.with_suffix(filename.suffix + suffix)
    assert not temp_filename.exists()
    with open(temp_filename, mode) as f:
        try:
            yield f
        except BaseException:
            try:
                f.close()
                temp_filename.unlink()
            except BaseException:
                pass
            raise
        else:
            f.close()
            temp_filename.rename(filename)
