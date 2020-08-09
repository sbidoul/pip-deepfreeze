import json
from typing import Optional, cast

from packaging.version import Version

from .compat import TypedDict, resource_as_file, resource_files
from .utils import check_output, log_error, log_warning, shlex_join

EnvInfo = TypedDict(
    "EnvInfo",
    {
        "in_virtualenv": bool,
        "include_system_site_packages": bool,
        "has_pkg_resources": bool,
        "has_importlib_metadata": bool,
        "pip_version": Optional[str],
        "setuptools_version": Optional[str],
        "wheel_version": Optional[str],
    },
)


def _get_env_info(python: str) -> EnvInfo:
    with resource_as_file(
        resource_files("pip_deepfreeze").joinpath(  # type: ignore
            "env_info_json.py"
        )
    ) as pip_list_json:
        return cast(EnvInfo, json.loads(check_output([python, str(pip_list_json)])))


def check_env(python: str) -> bool:
    env_info = _get_env_info(python)
    if not env_info.get("in_virtualenv"):
        log_error(f"{python} is not in a virtualenv, refusing to start.")
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
