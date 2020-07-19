import contextlib
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import IO, Any, Dict, Iterator, List, Optional, Sequence, Union

import typer

from .compat import shlex_join


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


def log_info(msg: str, nl: bool = True) -> None:
    typer.secho(msg, err=True, nl=nl)


def log_warning(msg: str) -> None:
    typer.secho(msg, fg=typer.colors.YELLOW, err=True)


def log_error(msg: str) -> None:
    typer.secho(msg, fg=typer.colors.RED, err=True)


def check_call(cmd: Sequence[Union[str, Path]], cwd: Optional[Path] = None) -> int:
    try:
        return subprocess.check_call(cmd, cwd=cwd)
    except CalledProcessError:
        cmd_str = shlex_join(str(item) for item in cmd)
        log_error(f"Error running: {cmd_str}.")
        raise typer.Exit(1)


def check_output(
    cmd: Sequence[Union[str, Path]],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, universal_newlines=True, env=env)
    except CalledProcessError:
        cmd_str = shlex_join(str(item) for item in cmd)
        log_error(f"Error running: {cmd_str}.")
        raise typer.Exit(1)
