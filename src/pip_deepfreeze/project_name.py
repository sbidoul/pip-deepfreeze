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
from typing import Optional

from packaging.utils import NormalizedName, canonicalize_name

from .pyproject_toml import PyProjectToml, load_pyproject_toml
from .utils import check_call, check_output, log_info


@lru_cache(maxsize=1)
def get_project_name(python: str, project_root: Path) -> NormalizedName:
    log_info("Getting project name..", nl=False)
    pyproject_toml = load_pyproject_toml(project_root)
    name = (
        get_project_name_from_pyproject_toml_pep621(pyproject_toml)
        or get_project_name_from_setup_cfg(project_root, pyproject_toml)
        or get_project_name_from_pyproject_toml_flit(pyproject_toml)
        or get_project_name_from_pep517(python, project_root)
    )
    log_info(" " + name)
    return canonicalize_name(name)


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
    project_name = (
        pyproject_toml.get("tool", {}).get("flit", {}).get("metadata", {}).get("module")
    )
    if not project_name:
        return None
    return str(project_name)


def get_project_name_from_pyproject_toml_pep621(
    pyproject_toml: Optional[PyProjectToml],
) -> Optional[str]:
    log_info(".", nl=False)
    if not pyproject_toml:
        return None
    project_name = pyproject_toml.get("project", {}).get("name")
    if not project_name:
        return None
    return str(project_name)


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
                "pep517==0.8.2",  # because we use an undocumented function of pep517
            ]
        )
        log_info(".", nl=False)
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
