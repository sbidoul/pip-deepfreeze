from __future__ import unicode_literals

import os
import subprocess
import sys

import pytest


@pytest.fixture
def virtualenv_python(tmp_path, testpkgs):
    """Return a python executable path within an isolated virtualenv, using a pip
    version that has the new resolver."""
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv)])
    if os.name == "nt":
        python = venv / "Scripts" / "python.exe"
    else:
        python = venv / "bin" / "python"
    # use latest pip
    subprocess.check_call(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
            "-U",
            "pip",
            "setuptools<71",  # https://github.com/pypa/setuptools/issues/4516
            "wheel",
        ]
    )
    return str(python)


@pytest.fixture
def virtualenv_python_with_pytest_cov(tmp_path):
    """Return a python executable path within an isolated virtualenv."""
    venv = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv)])
    if os.name == "nt":
        python = venv / "Scripts" / "python.exe"
    else:
        python = venv / "bin" / "python"
    subprocess.check_call([str(python), "-m", "pip", "install", "pytest-cov"])
    return str(python)


@pytest.fixture
def virtualenv_python_with_system_site_packages(tmp_path):
    """Return a python executable path within an isolated virtualenv."""
    venv = tmp_path / "venv"
    subprocess.check_call(
        [sys.executable, "-m", "virtualenv", str(venv), "--system-site-packages"]
    )
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
        dict(name="pkgb", install_requires=["pkga<0.0.1"]),
        dict(name="pkgc", version="0.0.1"),
        dict(name="pkgc", version="0.0.2"),
        dict(name="pkgc", version="0.0.3"),
        dict(
            name="pkgd",
            install_requires=["pkga"],
            extras_require={"c": ["pkgc<0.0.3"], "b": ["pkgb"]},
        ),
        dict(name="pkge", install_requires=["pkgd[b,c]"]),
        dict(name="pkg-F.G_H"),  # to test name normalization
    ]

    testpkgs_dir = tmp_path_factory.mktemp("testpkgs")

    # Download some wheels so we can build pyproject-based packages without network.
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "setuptools<71",  # https://github.com/pypa/setuptools/issues/4516
            "wheel",
            "--wheel-dir",
            str(testpkgs_dir),
        ]
    )

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
                "--no-index",
                "--find-links",
                str(testpkgs_dir),
                "--no-deps",
                str(setup_py_dir),
                "--wheel-dir",
                str(testpkgs_dir),
            ],
        )

    return testpkgs_dir.as_uri()
