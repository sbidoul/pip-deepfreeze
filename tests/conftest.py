import subprocess
import sys

import pytest


@pytest.fixture
def virtualenv_python(tmp_path):
    """Return a python executable path within an isolated virtualenv."""
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", venv])
    return venv / "bin" / "python"
