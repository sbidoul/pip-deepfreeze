import contextlib
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import IO, Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union

import typer

from .compat import shlex_join


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
            with open(temp_filename) as fafter:
                after = fafter.read()
            before = None  # type: Optional[str]
            if filename.exists():
                with open(filename) as fbefore:
                    before = fbefore.read()
                filename.unlink()
            temp_filename.rename(filename)
            if before is None:
                log_notice(f"Created {filename}")
            elif before != after:
                log_notice(f"Updated {filename}")
            else:
                log_info(f"No change to {filename}")


_verbosity = 0


def increase_verbosity() -> None:
    global _verbosity
    _verbosity += 1


def decrease_verbosity() -> None:
    global _verbosity
    _verbosity -= 1


def log_debug(msg: str) -> None:
    if _verbosity > 0:
        typer.secho(msg, dim=True, err=True)


def log_info(msg: str, nl: bool = True) -> None:
    typer.secho(msg, fg=typer.colors.BRIGHT_BLUE, err=True, nl=nl)


def log_notice(msg: str, nl: bool = True) -> None:
    typer.secho(msg, fg=typer.colors.GREEN, err=True, nl=nl)


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


def comma_split(s: Optional[str]) -> List[str]:
    if not s:
        return []
    s = s.strip()
    if not s:
        return []
    items = [item.strip() for item in s.split(",")]
    return [item for item in items if item]


def make_project_name_with_extras(
    project_name: str, extras: Optional[Iterable[str]]
) -> str:
    if not extras:
        return project_name
    else:
        return project_name + "[" + ",".join(extras) + "]"
