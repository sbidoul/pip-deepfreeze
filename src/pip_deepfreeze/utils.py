import atexit
import contextlib
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from typing import IO, Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union

import httpx
import typer


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
    except CalledProcessError as e:
        cmd_str = shlex.join(str(item) for item in cmd)
        log_error(f"Error running: {cmd_str}.")
        raise typer.Exit(1) from e


def check_output(
    cmd: Sequence[Union[str, Path]],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, text=True, env=env)
    except CalledProcessError as e:
        cmd_str = shlex.join(str(item) for item in cmd)
        log_error(f"Error running: {cmd_str}.")
        raise typer.Exit(1) from e


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


_NORMALIZE_REQ_LINE_RE = re.compile(
    r"^(?P<name>[a-zA-Z0-9-_.\[\]]+)(?P<arobas>\s*@\s*)(?P<rest>.*)$"
)


def normalize_req_line(req_line: str) -> str:
    """Normalize a requirement line so they are comparable.

    This is a little hack because some requirements.txt generator such
    as pip-requirements-parser dont always generate the exact same
    output as pip freeze.
    """
    mo = _NORMALIZE_REQ_LINE_RE.match(req_line)
    if not mo:
        return req_line
    return mo.group("name") + " @ " + mo.group("rest")


def get_temp_path_in_dir(dir: Path, prefix: str, suffix: str) -> Path:
    """Create a temporary file in a directory and register it for deletion at exit."""
    with tempfile.NamedTemporaryFile(
        dir=dir, prefix=prefix, suffix=suffix, delete=False
    ) as tf:
        path = Path(tf.name)
        atexit.register(path.unlink)
        return path


class HttpFetcher:
    def __init__(self) -> None:
        self._client = httpx.Client()

    def __call__(self, url: str) -> str:
        resp = self._client.get(url)
        resp.raise_for_status()
        return resp.text


def run_commands(commands: Sequence[str], cwd: Path, command_type: str) -> None:
    for command in commands:
        log_info(f"Running {command_type} command: {command}")
        result = subprocess.run(command, shell=True, check=False, cwd=cwd)
        if result.returncode != 0:
            raise SystemExit(
                f"{command_type.capitalize()} command {command} "
                "failed with exit code {result.returncode}"
            )


def make_requirements_path(project_root: Path, extra: Optional[str]) -> Path:
    if extra:
        return project_root / f"requirements-{extra}.txt"
    else:
        return project_root / "requirements.txt"


def make_requirements_paths(
    project_root: Path, extras: Sequence[str]
) -> Iterator[Path]:
    yield make_requirements_path(project_root, None)
    for extra in extras:
        yield make_requirements_path(project_root, extra)
