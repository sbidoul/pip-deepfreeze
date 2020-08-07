import subprocess
from typing import Optional

from packaging.version import InvalidVersion, Version

from .utils import log_error, log_warning, shlex_join


def _parse_pip_version(version_line: str) -> Optional[Version]:
    try:
        version_chunks = version_line.split()
        if len(version_chunks) < 2:
            raise InvalidVersion()
        return Version(version_chunks[1])
    except InvalidVersion:
        log_warning(f"Could not detect pip version in pip output: {version_line!r}.")
        return None


def _check_pip(python: str) -> bool:
    try:
        version_line = subprocess.check_output(
            [python, "-m", "pip", "--version"],
            universal_newlines=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        log_error(f"pip is not available to {python}. Please install it.")
        return False
    else:
        pip_version = _parse_pip_version(version_line)
        if pip_version and pip_version < Version("20.1"):
            install_cmd = shlex_join([python, "-m", "pip", "install", "pip>=20.1"])
            log_warning(
                f"pip-deepfreeze works best with pip>=20.1, "
                f"in particular if you use direct URL references. "
                f"You can install it with {install_cmd}."
            )
        return True


def _check_pkg_resources(python: str) -> bool:
    try:
        subprocess.check_output(
            [python, "-c", "import pkg_resources"], stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        install_cmd = shlex_join([python, "-m", "pip", "install", "setuptools"])
        log_error(
            f"pkg_resources is not available to {python}. It is currently "
            f"required by pip-deepfreeze. You can install it with {install_cmd}."
        )
        return False
    else:
        return True


def _check_wheel(python: str) -> bool:
    try:
        subprocess.check_output(
            [python, "-c", "import wheel"], stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        install_cmd = shlex_join([python, "-m", "pip", "install", "wheel"])
        log_warning(
            f"wheel is not available to {python}. "
            f"pip currently works best when the wheel package is installed, "
            f"in particular if you use direct URL references. "
            f"You can install it with {install_cmd}."
        )
    return True


def check_env(python: str) -> bool:
    pip_ok = _check_pip(python)
    pkg_resources_ok = _check_pkg_resources(python)
    wheel_ok = _check_wheel(python)
    return pip_ok and pkg_resources_ok and wheel_ok
