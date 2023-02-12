import json
import subprocess
from importlib.resources import path as resource_path
from typing import Optional, cast

from packaging.version import Version

from .compat import TypedDict, shlex_join
from .utils import log_error, log_warning

EnvInfo = TypedDict(
    "EnvInfo",
    {
        "in_virtualenv": Optional[bool],
        "include_system_site_packages": Optional[bool],
        "has_pkg_resources": Optional[bool],
        "has_importlib_metadata": Optional[bool],
        "pip_version": Optional[str],
        "setuptools_version": Optional[str],
        "wheel_version": Optional[str],
    },
    total=False,
)


def _get_env_info(python: str) -> EnvInfo:
    with resource_path("pip_deepfreeze", "env_info_json.py") as env_info_json_script:
        try:
            env_info_json = subprocess.check_output(
                [python, str(env_info_json_script)], universal_newlines=True
            )
        except subprocess.CalledProcessError:
            return EnvInfo(in_virtualenv=False)
        else:
            return cast(EnvInfo, json.loads(env_info_json))


def check_env(python: str) -> bool:
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
    if not env_info.get("has_pkg_resources"):
        setuptools_install_cmd = shlex_join(
            [python, "-m", "pip", "install", "setuptools"]
        )
        log_error(
            f"pkg_resources is not available to {python}. It is currently "
            f"required by pip-deepfreeze. "
            f"You can install it with {setuptools_install_cmd}."
        )
        return False
    pip_version = env_info.get("pip_version")
    if not pip_version:
        log_error(f"pip is not available to {python}. Please install it.")
        return False
    if Version(pip_version) < Version("20.1"):
        pip_install_cmd = shlex_join([python, "-m", "pip", "install", "pip>=20.1"])
        log_warning(
            f"pip-deepfreeze works best with pip>=20.1, "
            f"in particular if you use direct URL references. "
            f"You can upgrade pip it with {pip_install_cmd}."
        )
    if not env_info.get("wheel_version"):
        wheel_install_cmd = shlex_join([python, "-m", "pip", "install", "wheel"])
        log_warning(
            f"wheel is not available to {python}. "
            f"pip currently works best when the wheel package is installed, "
            f"in particular if you use direct URL references. "
            f"You can install it with {wheel_install_cmd}."
        )
    return True
