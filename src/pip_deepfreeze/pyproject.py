"""Determine if a directory is a Python project."""
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def is_pyproject(project_root: Path) -> bool:
    pyproject_toml_path = project_root / "pyproject.toml"
    setup_py_path = project_root / "setup.py"
    setup_cfg_path = project_root / "setup.cfg"
    return (
        pyproject_toml_path.is_file()
        or setup_py_path.is_file()
        or setup_cfg_path.is_file()
    )
