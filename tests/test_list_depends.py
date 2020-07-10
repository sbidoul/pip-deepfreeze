import os
import subprocess

import pytest

HERE = os.path.dirname(__file__)
TESTPKGS_DIR = os.path.join(HERE, "testpkgs")
LIST_DEPENDS = os.path.join(HERE, "..", "src", "pip_deepfreeze", "_list_depends.py")


@pytest.mark.parametrize(
    "to_install, distribution, expected",
    [(["pkga"], "pkga", []), (["pkgb"], "pkgb", ["pkga"]), (["pkgb"], "pkga", [])],
)
def test_list_depends(to_install, distribution, expected, virtualenv_python):
    # We need to install pytest-cov so subprocess coverage works.
    subprocess.check_call(
        [virtualenv_python, "-m", "pip", "install", "-f", TESTPKGS_DIR, "pytest-cov"]
        + to_install
    )
    depends = (
        subprocess.check_output(
            [virtualenv_python, LIST_DEPENDS, distribution], universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == expected
