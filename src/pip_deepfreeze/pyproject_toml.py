from pathlib import Path
from typing import Any, MutableMapping, Optional

from .compat import tomllib

PyProjectToml = MutableMapping[str, Any]


def load_pyproject_toml(project_root: Path) -> Optional[PyProjectToml]:
    pyproject_toml_path = project_root / "pyproject.toml"
    if not pyproject_toml_path.is_file():
        return None
    return tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
