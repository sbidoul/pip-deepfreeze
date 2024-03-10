import json
import shlex
import subprocess
import sys
from functools import lru_cache
from importlib.metadata import version
from typing import Optional, Tuple, TypedDict, cast

import typer
from packaging.version import Version

from .compat import importlib_resources
from .utils import log_error, log_warning


class EnvInfo(TypedDict, total=False):
    in_virtualenv: Optional[bool]
    include_system_site_packages: Optional[bool]
    has_pkg_resources: Optional[bool]
    has_importlib_metadata: Optional[bool]
    pip_version: Optional[str]
    setuptools_version: Optional[str]
    wheel_version: Optional[str]
    python_version: str


@lru_cache
def _get_env_info(python: str) -> EnvInfo:
    with importlib_resources.as_file(
        importlib_resources.files("pip_deepfreeze").joinpath("env-info-json.py")
    ) as env_info_json_script:
        try:
            env_info_json = subprocess.check_output(
                [python, str(env_info_json_script)], text=True
            )
        except subprocess.CalledProcessError:
            return EnvInfo(in_virtualenv=False)
        else:
            return cast(EnvInfo, json.loads(env_info_json))


@lru_cache
def get_pip_version(python: str) -> Version:
    pip_version = _get_env_info(python).get("pip_version")
    if pip_version:
        return Version(pip_version)
    return Version(version("pip"))


@lru_cache
def get_pip_command(python: str) -> Tuple[str, ...]:
    env_pip_version = _get_env_info(python).get("pip_version")
    if env_pip_version:
        # pip is installed in the target environment, let's use it
        return (python, "-m", "pip")
    if not local_pip_compatible(python):
        log_error(
            f"pip is not available to {python}, and the pip version. "
            f"installed the pip-deepfreeze environment is not compatible with it. "
            f"Please install pip in the target environment."
        )
        raise typer.Exit(1)
    return (sys.executable, "-m", "pip", "--python", python, "--no-input")


@lru_cache
def get_python_version_info(python: str) -> Tuple[int, ...]:
    python_version = _get_env_info(python).get("python_version")
    assert python_version
    return tuple(map(int, python_version.split(".", 1)))


@lru_cache
def local_pip_compatible(python: str) -> bool:
    cmd = [sys.executable, "-m", "pip", "--python", python, "--version"]
    return subprocess.call(cmd) == 0


def check_env(python: str) -> bool:
    _get_env_info.cache_clear()
    env_info = _get_env_info(python)
    if not env_info.get("in_virtualenv"):
        log_error(
            f"{python} is not in a virtualenv, refusing to start. "
            f"See https://github.com/sbidoul/pip-deepfreeze/issues/47 "
            f"for hints and discussion."
        )
        return False
    if env_info.get("include_system_site_packages"):
        log_error(
            f"{python} is in a virtualenv that includes system site packages, "
            f"refusing to start."
        )
        return False
    pip_version = env_info.get("pip_version")
    if not env_info.get("has_pkg_resources") and (
        (
            # target pip does not have pip inspect: we need pkg_resources to
            # inspect with env-info-json.py
            pip_version and Version(pip_version) < Version("22.2")
        )
        or (
            # pip not installed in target python env and local pip is not compatible
            # with target python, so we'll need pkg_resources to inspect with
            # env-info-json.py
            not pip_version and not local_pip_compatible(python)
        )
    ):
        setuptools_install_cmd = shlex.join(
            [python, "-m", "pip", "install", "setuptools"]
        )
        pip_upgrade_cmd = shlex.join(
            [python, "-m", "pip", "install", "--upgrade", "pip"]
        )
        log_error(
            f"pkg_resources is not available to {python}. It is currently "
            f"required by pip-deepfreeze unless you have pip>=22.2. "
            f"You can either upgrade pip with '{pip_upgrade_cmd}' or "
            f"installs pkg_resources with '{setuptools_install_cmd}'."
        )
        return False
    # Testing for pip must be done after testing for pkg_resources, because
    # pkg_resources is needed to obtain the pip version for python < 3.8.
    if not pip_version and not local_pip_compatible(python):
        log_error(f"pip is not available to {python}. Please install it.")
        return False
    if pip_version and Version(pip_version) < Version("20.1"):
        pip_install_cmd = shlex.join([python, "-m", "pip", "install", "pip>=20.1"])
        log_warning(
            f"pip-deepfreeze works best with pip>=20.1, "
            f"in particular if you use direct URL references. "
            f"You can upgrade pip it with '{pip_install_cmd}'."
        )
    if (
        not env_info.get("wheel_version")
        and pip_version
        and Version(pip_version) < Version("23.1")
    ):
        wheel_install_cmd = shlex.join([python, "-m", "pip", "install", "wheel"])
        log_warning(
            f"wheel is not available to {python}. "
            f"pip currently works best when the wheel package is installed, "
            f"in particular if you use direct URL references. "
            f"You can install it with '{wheel_install_cmd}'."
        )
    return True
