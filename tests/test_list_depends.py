import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(__file__)
TESTPKGS_DIR = os.path.join(HERE, "testpkgs")
LIST_DEPENDS = os.path.join(HERE, "..", "src", "pip_deepfreeze", "_list_depends.py")

# /!\ this test file must be python 2 compatible and must not rely on conftest.py /!\


@pytest.mark.parametrize(
    "to_install, distribution, expected",
    [(["pkga"], "pkga", []), (["pkgb"], "pkgb", ["pkga"]), (["pkgb"], "pkga", [])],
)
def test_list_depends(to_install, distribution, expected, tmp_path):
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv)])
    # We need to install pytest-cov so subprocess coverage works.
    subprocess.check_call(
        [str(venv / "bin" / "pip"), "install", "-f", TESTPKGS_DIR, "pytest-cov"]
        + to_install
    )
    depends = (
        subprocess.check_output(
            [str(venv / "bin" / "python"), LIST_DEPENDS, distribution],
            universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == expected
