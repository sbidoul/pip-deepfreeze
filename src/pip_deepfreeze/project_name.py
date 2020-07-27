"""Get the project name as quickly as we can.

Analyze the configuration files for some known build backends
(setuptools' setup.cfg, flit, generic PEP 621). Fallback to a slower PEP
517 metadata preparation.
"""
import configparser
import os
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, MutableMapping, Optional

import toml

from .utils import check_call, check_output, log_info

PyProjectToml = MutableMapping[str, Any]


@lru_cache(maxsize=1)
def get_project_name(python: str, project_root: Path) -> str:
    log_info("Getting project name..", nl=False)
    pyproject_toml = _load_pyproject_toml(project_root)
    name = (
        get_project_name_from_setup_cfg(project_root, pyproject_toml)
        or get_project_name_from_pyproject_toml_flit(pyproject_toml)
        or get_project_name_from_pyproject_toml_pep621(pyproject_toml)
        or get_project_name_from_pep517(python, project_root)
    )
    log_info(" " + name)
    return name


def _load_pyproject_toml(project_root: Path) -> Optional[PyProjectToml]:
    log_info(".", nl=False)
    pyproject_toml_path = project_root / "pyproject.toml"
    if not pyproject_toml_path.is_file():
        return None
    return toml.loads(pyproject_toml_path.read_text())


def _get_build_backend(pyproject_toml: Optional[PyProjectToml]) -> Optional[str]:
    if not pyproject_toml:
        return None
    build_backend = pyproject_toml.get("build-system", {}).get("build-backend", None)
    if not build_backend:
        return None
    return str(build_backend)


def get_project_name_from_setup_cfg(
    project_root: Path, pyproject_toml: Optional[PyProjectToml]
) -> Optional[str]:
    log_info(".", nl=False)
    if _get_build_backend(pyproject_toml) not in (
        None,
        "setuptools.build_meta",
        "setuptools.build_meta:__legacy__",
    ):
        return None
    setup_cfg_path = project_root / "setup.cfg"
    if not setup_cfg_path.is_file():
        return None
    try:
        setup_cfg = configparser.ConfigParser()
        setup_cfg.read(setup_cfg_path)
        return setup_cfg.get("metadata", "name")
    except configparser.Error:
        return None


def get_project_name_from_pyproject_toml_flit(
    pyproject_toml: Optional[PyProjectToml],
) -> Optional[str]:
    log_info(".", nl=False)
    if _get_build_backend(pyproject_toml) not in (
        "flit_core.buildapi",
        "flit.buildapi",
    ):
        return None
    assert pyproject_toml
    return str(
        pyproject_toml.get("tool", {}).get("flit", {}).get("metadata", {}).get("module")
    )


def get_project_name_from_pyproject_toml_pep621(
    pyproject_toml: Optional[PyProjectToml],
) -> Optional[str]:
    log_info(".", nl=False)
    if not _get_build_backend(pyproject_toml):
        return None
    assert pyproject_toml
    return str(pyproject_toml.get("project", {}).get("name"))


def get_project_name_from_pep517(python: str, project_root: Path) -> str:
    """Get a project name building metadata using pep517.

    We build in a separate process so we support python 2 builds.
    """
    with TemporaryDirectory() as pep517_install_dir:
        # first install pep517
        log_info(".", nl=False)
        check_call(
            [
                python,
                "-m",
                "pip",
                "-q",
                "install",
                "--target",
                pep517_install_dir,
                "pep517==0.8.2",
            ]
        )
        log_info(".", nl=False)
        # TODO this uses an undocumented function of pep517
        name = check_output(
            [
                python,
                "-c",
                "from pep517.meta import load; import sys; "
                "sys.stdout.write(load(sys.argv[1]).metadata['Name'])",
                str(project_root),
            ],
            env=dict(os.environ, PYTHONPATH=pep517_install_dir),
        )
        return name
