from __future__ import unicode_literals

import os
import subprocess
import sys

import pytest


@pytest.fixture
def virtualenv_python(tmp_path):
    """Return a python executable path within an isolated virtualenv."""
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv)])
    if os.name == "nt":
        python = venv / "Scripts" / "python.exe"
    else:
        python = venv / "bin" / "python"
    return str(python)


@pytest.fixture(scope="session")
def testpkgs(tmp_path_factory):
    """Create test wheels and return the temp dir where they are stored."""
    # setup.py keywords for wheels to create
    testpkgs_kw = [
        dict(name="pkga"),
        dict(name="pkgb", install_requires=["pkga"]),
        dict(name="pkgc", version="0.0.1"),
        dict(name="pkgc", version="0.0.2"),
        dict(name="pkgc", version="0.0.3"),
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

    return testpkgs_dir.as_uri()
