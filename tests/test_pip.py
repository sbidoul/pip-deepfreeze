import subprocess
import textwrap
from typing import Iterable, Iterator

import pytest

from pip_deepfreeze.pip import (
    pip_freeze,
    pip_freeze_dependencies,
    pip_uninstall,
    pip_upgrade_project,
)


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
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            testpkgs,
        ]
        + to_install
    )
    assert list(pip_freeze(virtualenv_python)) == expected


@pytest.mark.parametrize(
    "install_requires, other_installs, expected",
    [
        ([], [], [[], []]),
        ([], ["pkgc"], [[], ["pkgc==0.0.3"]]),
        (["pkga"], [], [["pkga==0.0.0"], []]),
        (["pkgb"], [], [["pkga==0.0.0", "pkgb==0.0.0"], []]),
        (["pkgb"], ["pkgc"], [["pkga==0.0.0", "pkgb==0.0.0"], ["pkgc==0.0.3"]]),
    ],
)
def test_pip_freeze_dependencies(
    install_requires, other_installs, expected, virtualenv_python, testpkgs, tmp_path
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
            "--find-links",
            testpkgs,
            "-e",
            str(tmp_path),  # str required for py < 3.8 on windows
        ]
        + other_installs
    )
    assert list(pip_freeze_dependencies(virtualenv_python, tmp_path)) == expected


@pytest.mark.parametrize(
    "to_install, to_uninstall, expected",
    [
        (["pkga==0.0.0"], ["pkga"], []),
        (["pkgb==0.0.0"], ["pkga"], ["pkgb==0.0.0"]),
        ([], [], []),
    ],
)
def test_pip_uninstall(to_install, to_uninstall, expected, virtualenv_python, testpkgs):
    if to_install:
        subprocess.call(
            [
                virtualenv_python,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--find-links",
                testpkgs,
            ]
            + to_install
        )
    pip_uninstall(virtualenv_python, to_uninstall)
    assert list(pip_freeze(virtualenv_python)) == expected


def _freeze_filter(reqs: Iterable[str]) -> Iterator[str]:
    """Filter out comments and -e."""
    for req in reqs:
        if req.startswith("#"):
            continue
        if req.startswith("-e"):
            continue
        yield req


def test_pip_upgrade_project(virtualenv_python, testpkgs, tmp_path):
    constraints = tmp_path / "requirements.txt.df"
    # First install, pkgc frozen to 0.0.1.
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=["pkgc"],
            )
            """
        )
    )
    constraints.write_text(f"--no-index\n--find-links {testpkgs}\npkgc==0.0.1")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == ["pkgc==0.0.1"]
    # Upgrade pkgc by adding a different constraint.
    constraints.write_text(f"--no-index\n--find-links {testpkgs}\npkgc<=0.0.2")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == ["pkgc==0.0.2"]
    # Upgrade pkgc to latest version by removing it from constraints.
    constraints.write_text(f"--no-index\n--find-links {testpkgs}")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == ["pkgc==0.0.3"]
    # Remove dependency from setup.py but it is still in frozen requirements,
    # the upgrade procedure does not remove it.
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=[],
            )
            """
        )
    )
    constraints.write_text(f"--no-index\n--find-links {testpkgs}\npkgc==0.0.3")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == ["pkgc==0.0.3"]
    # Remove dependency from frozen requirements, check the upgrade procedure
    # does not remove it (it is now an unrelated package which we leave alone).
    constraints.write_text(f"--no-index\n--find-links {testpkgs}")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == ["pkgc==0.0.3"]


@pytest.mark.xfail(reason="we don't use constraints for now.")
def test_pip_upgrade_constraint_not_a_dep(virtualenv_python, testpkgs, tmp_path):
    """Test upgrading does not install constraints that are not dependencies."""
    constraints = tmp_path / "requirements.txt.df"
    # First install, pkgc frozen to 0.0.1.
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(name="theproject")
            """
        )
    )
    constraints.write_text(f"--no-index\n--find-links {testpkgs}\npkgc==0.0.1")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == []


def test_pip_upgrade_vcs_url(virtualenv_python, tmp_path):
    """Test upgrading a VCS URL."""
    constraints = tmp_path / "requirements.txt.df"
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=["toml"],
            )
            """
        )
    )
    # install tag 0.10.0
    constraints.write_text("--no-index\ntoml @ git+https://github.com/uiri/toml@0.10.0")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == [
        "toml @ git+https://github.com/uiri/toml"
        "@4935f616ef78c35a968b2473e806d7049eba9af1"
    ]
    # upgrade to tag 0.10.1
    constraints.write_text("toml @ git+https://github.com/uiri/toml@0.10.1")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == [
        "toml @ git+https://github.com/uiri/toml"
        "@a86fc1fbd650a19eba313c3f642c9e2c679dc8d6"
    ]
