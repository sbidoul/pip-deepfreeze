from __future__ import unicode_literals

import os
import subprocess
import textwrap

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


def test_list_depends_script_downgrade_dep(tmp_path, virtualenv_python, testpkgs):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(name="theproject", install_requires=["pkgc>=0.0.3"])
            """
        )
    )
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "-e",
            str(tmp_path),
            "-f",
            str(testpkgs),
        ]
    )
    depends = (
        subprocess.check_output(
            [virtualenv_python, LIST_DEPENDS_SCRIPT, "theproject"],
            universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == ["pkgc"]
    # Change to ask for downgrade of pkgc and try list depends again.
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(name="theproject", install_requires=["pkgc<0.0.3"])
            """
        )
    )
    subprocess.check_call(
        [virtualenv_python, "setup.py", "egg_info"], cwd=str(tmp_path)
    )
    depends = (
        subprocess.check_output(
            [virtualenv_python, LIST_DEPENDS_SCRIPT, "theproject"],
            universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == ["pkgc"]


def test_list_depends_script_missing_dep(virtualenv_python, testpkgs):
    # We need to install pytest-cov so subprocess coverage works.
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--find-links",
            testpkgs,
            "pytest-cov",
            "pkgb",
        ]
    )
    subprocess.check_call(
        [virtualenv_python, "-m", "pip", "uninstall", "--yes", "pkga"]
    )
    depends = (
        subprocess.check_output(
            [virtualenv_python, LIST_DEPENDS_SCRIPT, "pkgb"], universal_newlines=True,
        )
        .strip()
        .split()
    )
    assert depends == []
