import os
import subprocess

import pytest

# /!\ this test file must be python 2 compatible /!\
LIST_DEPENDS_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "src", "pip_deepfreeze", "list_depends_script.py"
)


@pytest.mark.parametrize(
    "to_install, distribution, expected",
    [
        (["pkga"], "pkga", []),
        (["pkgb"], "pkgb", ["pkga"]),
        (["pkgb"], "pkga", []),
        (["--no-deps", "pkgb"], "pkgb", []),
    ],
)
def test_list_depends_script(
    to_install, distribution, expected, virtualenv_python, testpkgs
):
    # We need to install pytest-cov so subprocess coverage works.
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
            "pytest-cov",
        ]
        + to_install
    )
    depends = (
        subprocess.check_output(
            [virtualenv_python, LIST_DEPENDS_SCRIPT, distribution],
            universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == expected
