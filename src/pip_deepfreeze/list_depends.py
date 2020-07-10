import subprocess
from pathlib import Path
from typing import Set

from .req_parser import canonicalize_name
from .utils import split_lines


def list_depends(python: str, project_name: str) -> Set[str]:
    list_depends_script = Path(__file__).parent / "list_depends_script.py"
    dependencies = split_lines(
        subprocess.check_output(
            [python, list_depends_script, project_name], universal_newlines=True
        )
    )
    return {canonicalize_name(d) for d in dependencies}
