import subprocess
import textwrap

import pytest

from pip_deepfreeze.pip import pip_freeze, pip_freeze_dependencies, pip_uninstall


@pytest.mark.parametrize(
    "to_install, expected",
    [
        ([], []),
        (["pkga==0.0.0"], ["pkga==0.0.0"]),
        (["pkgb==0.0.0"], ["pkga==0.0.0", "pkgb==0.0.0"]),
    ],
)
def test_pip_freeze(to_install, expected, virtualenv_python, testpkgs):
    subprocess.call(
        [virtualenv_python, "-m", "pip", "install", "--no-index", "-f", testpkgs]
        + to_install
    )
    assert list(pip_freeze(virtualenv_python)) == expected


@pytest.mark.parametrize(
    "install_requires, expected",
    [([], []), (["pkga"], ["pkga==0.0.0"]), (["pkgb"], ["pkga==0.0.0", "pkgb==0.0.0"])],
)
def test_pip_freeze_dependencies(
    install_requires, expected, virtualenv_python, testpkgs, tmp_path
):
    # note: complex dependency situations are tested in test_list_depends.py
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            f"""
            from setuptools import setup

            setup(
                name="theproject",
                install_requires={install_requires!r},
            )
            """
        )
    )
    subprocess.call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "-f",
            testpkgs,
            "-e",
            tmp_path,
        ]
    )
    assert list(pip_freeze_dependencies(virtualenv_python, tmp_path)) == expected


@pytest.mark.parametrize(
    "to_install, to_uninstall, expected",
    [(["pkga==0.0.0"], ["pkga"], []), (["pkgb==0.0.0"], ["pkga"], ["pkgb==0.0.0"])],
)
def test_pip_uninstall(to_install, to_uninstall, expected, virtualenv_python, testpkgs):
    subprocess.call(
        [virtualenv_python, "-m", "pip", "install", "--no-index", "-f", testpkgs]
        + to_install
    )
    pip_uninstall(virtualenv_python, to_uninstall)
    assert list(pip_freeze(virtualenv_python)) == expected
