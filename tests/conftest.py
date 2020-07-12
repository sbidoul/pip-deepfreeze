from __future__ import unicode_literals

import subprocess
import sys

import pytest


@pytest.fixture
def virtualenv_python(tmp_path):
    """Return a python executable path within an isolated virtualenv."""
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv)])
    return str(venv / "bin" / "python")


@pytest.fixture(scope="session")
def testpkgs(tmp_path_factory):
    """ Create test wheels and return the temp dir where they are stored."""
    # setup.py keywords for wheels to create
    testpkgs_kw = [
        dict(name="pkga"),
        dict(name="pkgb", install_requires=["pkga"]),
    ]

    testpkgs_dir = tmp_path_factory.mktemp("testpkgs")

    for testpkg_kw in testpkgs_kw:
        setup_py_dir = tmp_path_factory.mktemp("testpkg")
        (setup_py_dir / "setup.py").write_text(
            "from setuptools import setup; setup(**{!r})".format(testpkg_kw)
        )
        (setup_py_dir / "setup.cfg").write_text("[bdist_wheel]\nuniversal = 1")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                str(setup_py_dir),
                "--wheel-dir",
                str(testpkgs_dir),
            ],
        )

    return str(testpkgs_dir)
