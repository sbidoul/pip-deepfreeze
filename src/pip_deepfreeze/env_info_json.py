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
- python_version: str (major.minor)

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


try:
    import pkg_resources  # noqa
except ImportError:
    pkg_resources = None


if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    try:
        import importlib_metadata  # noqa
    except ImportError:
        importlib_metadata = None


def _get_version(dist_name):
    # type: (str) -> Optional[str]
    if importlib_metadata:
        try:
            return importlib_metadata.version(dist_name)
        except importlib_metadata.PackageNotFoundError:
            return None
    elif pkg_resources:
        try:
            return pkg_resources.get_distribution(dist_name).version
        except pkg_resources.DistributionNotFound:
            return None
    else:
        return None


def _load_pyvenv_cfg(pyvenv_cfg_path):
    # type: (str) -> Dict[str, str]
    pyvenv_cfg = {}
    with io.open(pyvenv_cfg_path, encoding="utf-8") as f:
        for line in f:
            key, _, value = line.partition("=")
            pyvenv_cfg[key.strip()] = value.strip()
    return pyvenv_cfg


def _find_pyvenv_cfg():
    # type: () -> Optional[Dict[str, str]]
    for pyvenv_cfg_path in (
        os.path.join(os.path.dirname(sys.executable), "pyvenv.cfg"),
        os.path.join(os.path.dirname(sys.executable), "..", "pyvenv.cfg"),
    ):
        try:
            pyvenv_cfg = _load_pyvenv_cfg(pyvenv_cfg_path)
        except IOError:
            continue
        if "home" not in pyvenv_cfg:
            continue
        return pyvenv_cfg
    return None


def main():
    # type: () -> None
    result = {}  # type: Dict[str, Union[Optional[str], bool]]
    pyvenv_cfg = _find_pyvenv_cfg()
    if pyvenv_cfg:
        result["in_virtualenv"] = True
        result["include_system_site_packages"] = (
            pyvenv_cfg.get("include-system-site-packages") != "false"
        )
    else:
        result["in_virtualenv"] = False
    result["has_pkg_resources"] = bool(pkg_resources)
    result["has_importlib_metadata"] = bool(importlib_metadata)
    result["pip_version"] = _get_version("pip")
    result["setuptools_version"] = _get_version("setuptools")
    result["wheel_version"] = _get_version("wheel")
    result["python_version"] = "%d.%d" % sys.version_info[:2]
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
