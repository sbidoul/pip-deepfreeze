from pathlib import Path
from typing import Any, MutableMapping, Optional

import toml

from .utils import log_info

PyProjectToml = MutableMapping[str, Any]


def load_pyproject_toml(project_root: Path) -> Optional[PyProjectToml]:
    log_info(".", nl=False)
    pyproject_toml_path = project_root / "pyproject.toml"
    if not pyproject_toml_path.is_file():
        return None
    return toml.loads(pyproject_toml_path.read_text(encoding="utf-8"))
