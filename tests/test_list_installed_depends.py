import subprocess
import textwrap

import pytest

from pip_deepfreeze.list_installed_depends import (
    list_installed_depends,
    list_installed_depends_by_extra,
)
from pip_deepfreeze.pip import pip_list


@pytest.mark.parametrize(
    "to_install, distribution, expected",
    [
        (["pkga"], "pkga", set()),
        (["pkgb"], "pkgb", {"pkga"}),
        (["pkgb"], "pkga", set()),
        (["--no-deps", "pkgb"], "pkgb", set()),
    ],
)
def test_list_installed_depends(
    to_install, distribution, expected, virtualenv_python, testpkgs
):
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
            *to_install,
        ]
    )
    assert list_installed_depends(pip_list(virtualenv_python), distribution) == expected


def test_list_installed_depends_downgrade_dep(tmp_path, virtualenv_python, testpkgs):
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
            "--no-index",
            "-f",
            str(testpkgs),
        ]
    )
    assert list_installed_depends(pip_list(virtualenv_python), "theproject") == {"pkgc"}
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
    assert list_installed_depends(pip_list(virtualenv_python), "theproject") == {"pkgc"}


def test_list_installed_depends_missing_dep(virtualenv_python, testpkgs):
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
            "pkgb",
        ]
    )
    subprocess.check_call(
        [virtualenv_python, "-m", "pip", "uninstall", "--yes", "pkga"]
    )
    assert list_installed_depends(pip_list(virtualenv_python), "pkgb") == set()


def test_list_installed_depends_extras(virtualenv_python, testpkgs, tmp_path):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=["pkga"],
                extras_require={
                    "b": ["pkgb"],
                    "c": ["pkgc"],
                },
            )
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
            str(tmp_path) + "[b,c]",
            "--no-index",
            "-f",
            str(testpkgs),
        ]
    )
    installed_dists = pip_list(virtualenv_python)
    assert list_installed_depends(installed_dists, "theproject") == {"pkga"}
    assert list_installed_depends(installed_dists, "theproject", extras=["b"]) == {
        "pkga",
        "pkgb",
    }
    assert list_installed_depends(installed_dists, "theproject", extras=["c"]) == {
        "pkga",
        "pkgc",
    }
    assert list_installed_depends(installed_dists, "theproject", extras=["c,b"]) == {
        "pkga",
        "pkgb",
        "pkgc",
    }


def test_list_installed_depends_by_extra(virtualenv_python, testpkgs, tmp_path):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=["pkga"],
                extras_require={
                    "b": ["pkgb"],
                    "c": ["pkgc"],
                },
            )
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
            str(tmp_path) + "[b,c]",
            "--no-index",
            "-f",
            str(testpkgs),
        ]
    )
    installed_dists = pip_list(virtualenv_python)
    assert list_installed_depends_by_extra(installed_dists, "theproject") == {
        None: {"pkga"},
        "b": {"pkgb"},
        "c": {"pkgc"},
    }


def test_list_installed_depends_new_extra(virtualenv_python, testpkgs, tmp_path):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=[],
            )
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
            "--no-index",
            "-f",
            str(testpkgs),
        ]
    )
    installed_dists = pip_list(virtualenv_python)
    assert list_installed_depends(installed_dists, "theproject", extras=["a"]) == set()
