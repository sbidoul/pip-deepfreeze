from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

from .compat import tomllib

PyProjectToml = MutableMapping[str, Any]


def load_pyproject_toml(project_root: Path) -> PyProjectToml | None:
    pyproject_toml_path = project_root / "pyproject.toml"
    if not pyproject_toml_path.is_file():
        return None
    return tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
