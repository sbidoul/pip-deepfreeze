import subprocess

import pytest

from pip_deepfreeze.pip import pip_freeze, pip_uninstall


@pytest.mark.parametrize(
    "to_install, expected",
    [
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
