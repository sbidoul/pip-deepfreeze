#!/usr/bin/env python
# type: ignore
"""Collect information about the python envionment.

Prints a json dictionary with the following keys:
- has_pkg_resources: bool
- has_importlib_metadata: bool
- pip_version: str
- setuptools_version: str
- wheel_version: str
- in_virtualenv: bool

This script must be python 2 compatible.
"""
import io
import json
import os
import sys

try:
    from typing import Dict, Optional, Union
except ImportError:
    pass


def _check_pkg_resources():
    # type: () -> bool
    try:
        import pkg_resources  # noqa
    except ImportError:
        return False
    else:
        return True


def _check_importlib_metadata():
    # type: () -> bool
    if sys.version_info >= (3, 8):
        return True
    else:
        try:
            import importlib_metadata  # noqa
        except ImportError:
            return False
        else:
            return True


def _get_version_importlib_metadata(dist_name):
    # type: (str) -> Optional[str]
    if sys.version_info >= (3, 8):
        from importlib import metadata as importlib_metadata
    else:
        import importlib_metadata

    try:
        return importlib_metadata.version(dist_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _get_version_pkg_resources(dist_name):
    # type: (str) -> Optional[str]
    import pkg_resources

    try:
        return pkg_resources.get_distribution(dist_name).version
    except pkg_resources.DistributionNotFound:
        return None


def _load_pyvenv_cfg(pyvenv_cfg_path):
    # type: (str) -> Dict[str, str]
    pyvenv_cfg = {}
    try:
        with io.open(pyvenv_cfg_path, encoding="utf-8") as f:
            for line in f:
                key, _, value = line.partition("=")
                pyvenv_cfg[key.strip()] = value.strip()
    except IOError:
        pass
    return pyvenv_cfg


def _find_pyvenv_cfg():
    # type: () -> Dict[str, str]
    for pyvenv_cfg_path in (
        os.path.join(os.path.dirname(sys.executable), "pyvenv.cfg"),
        os.path.join(os.path.dirname(sys.executable), "..", "pyvenv.cfg"),
    ):
        if not os.path.isfile(pyvenv_cfg_path):
            continue
        pyvenv_cfg = _load_pyvenv_cfg(pyvenv_cfg_path)
        return pyvenv_cfg
    return {}


def main():
    # type: () -> None
    result = {}  # type: Dict[str, Union[Optional[str], bool]]
    pyvenv_cfg = _find_pyvenv_cfg()
    result["in_virtualenv"] = bool(pyvenv_cfg.get("home"))
    result["include_system_site_packages"] = (
        pyvenv_cfg.get("include-system-site-packages") != "false"
    )
    result["has_pkg_resources"] = _check_pkg_resources()
    result["has_importlib_metadata"] = _check_importlib_metadata()
    _get_version = None
    if result["has_importlib_metadata"]:
        _get_version = _get_version_importlib_metadata
    elif result["has_pkg_resources"]:
        _get_version = _get_version_pkg_resources
    if _get_version:
        result["pip_version"] = _get_version("pip")
        result["setuptools_version"] = _get_version("setuptools")
        result["wheel_version"] = _get_version("wheel")
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
