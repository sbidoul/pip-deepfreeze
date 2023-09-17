import subprocess
import textwrap
from typing import Iterable, Iterator

import pytest
from packaging.requirements import Requirement

from pip_deepfreeze.pip import (
    _pip_list__env_info_json,
    _pip_list__pip_inspect,
    pip_freeze,
    pip_freeze_dependencies,
    pip_freeze_dependencies_by_extra,
    pip_list,
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
            *to_install,
        ]
    )
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == expected


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
    # note: complex dependency situations are tested in test_list_installed_depends.py
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
            tmp_path,
            *other_installs,
        ]
    )
    res = pip_freeze_dependencies(virtualenv_python, tmp_path)
    unneeded_reqs = res[-1]
    unneeded_reqs[:] = list(_freeze_filter(unneeded_reqs))
    assert list(res) == expected


@pytest.mark.parametrize(
    "install_requires, extras_require, other_installs, freeze_extras, expected",
    [
        ([], {}, [], [], [{None: []}, []]),
        ([], {}, ["pkgc"], [], [{None: []}, ["pkgc==0.0.3"]]),
        (["pkga"], {}, [], [], [{None: ["pkga==0.0.0"]}, []]),
        (["pkgb"], {}, [], [], [{None: ["pkga==0.0.0", "pkgb==0.0.0"]}, []]),
        (
            ["pkgb"],
            {},
            ["pkgc"],
            [],
            [{None: ["pkga==0.0.0", "pkgb==0.0.0"]}, ["pkgc==0.0.3"]],
        ),
        (
            ["pkgc"],
            {"b": ["pkgb"]},
            [],
            [],
            [{None: ["pkgc==0.0.3"]}, ["pkga==0.0.0", "pkgb==0.0.0"]],
        ),
        (
            ["pkgc"],
            {"b": ["pkgb"]},
            [],
            ["b"],
            [{None: ["pkgc==0.0.3"], "b": ["pkga==0.0.0", "pkgb==0.0.0"]}, []],
        ),
        # unknown extra "a"
        ([], {}, ["pkga"], ["a"], [{None: []}, ["pkga==0.0.0"]]),
    ],
)
def test_pip_freeze_dependencies_by_extra(
    install_requires,
    extras_require,
    other_installs,
    freeze_extras,
    expected,
    virtualenv_python,
    testpkgs,
    tmp_path,
):
    # note: complex dependency situations are tested in test_list_installed_depends.py
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            f"""
            from setuptools import setup

            setup(
                name="theproject",
                install_requires={install_requires!r},
                extras_require={extras_require!r},
            )
            """
        )
    )
    install = str(tmp_path)
    if extras_require:
        install += "[" + ",".join(extras_require.keys()) + "]"
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
            install,
            *other_installs,
        ]
    )
    res = pip_freeze_dependencies_by_extra(virtualenv_python, tmp_path, freeze_extras)
    unneeded_reqs = res[-1]
    unneeded_reqs[:] = list(_freeze_filter(unneeded_reqs))
    assert list(res) == expected


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
                *to_install,
            ]
        )
    pip_uninstall(virtualenv_python, to_uninstall)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == expected


def _freeze_filter(reqs: Iterable[str]) -> Iterator[str]:
    """Filter out comments and -e."""
    filters = ("#", "-e ", "pip==", "setuptools==", "wheel==", "distribute==")
    for req in reqs:
        if any(req.startswith(f) for f in filters):
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


def test_pip_upgrade_vcs_url(virtualenv_python, tmp_path, capfd):
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
    assert "Uninstalling dependencies to update" not in capfd.readouterr().err
    # reinstall, no change but different @url syntax
    constraints.write_text(
        "--no-index\n"
        "toml@git+https://github.com/uiri/toml@4935f616ef78c35a968b2473e806d7049eba9af1"
    )
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == [
        "toml @ git+https://github.com/uiri/toml"
        "@4935f616ef78c35a968b2473e806d7049eba9af1"
    ]
    assert "Uninstalling dependencies to update" not in capfd.readouterr().err
    # upgrade to tag 0.10.1
    constraints.write_text("toml @ git+https://github.com/uiri/toml@0.10.1")
    pip_upgrade_project(virtualenv_python, constraints, project_root=tmp_path)
    assert list(_freeze_filter(pip_freeze(virtualenv_python))) == [
        "toml @ git+https://github.com/uiri/toml"
        "@a86fc1fbd650a19eba313c3f642c9e2c679dc8d6"
    ]


@pytest.mark.parametrize(
    "pip_list_function", (_pip_list__env_info_json, _pip_list__pip_inspect, pip_list)
)
def test_pip_list(virtualenv_python, testpkgs, pip_list_function):
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "-f",
            testpkgs,
            "pkgb",
        ]
    )
    installed_dists = pip_list_function(virtualenv_python)
    assert set(installed_dists.keys()) == {"pkga", "pkgb", "pip", "wheel", "setuptools"}
    pkga_dist = installed_dists["pkga"]
    assert pkga_dist.name == "pkga"
    assert pkga_dist.version == "0.0.0"
    # assert pkga_dist.direct_url is None
    pkgb_dist = installed_dists["pkgb"]
    assert pkgb_dist.name == "pkgb"
    assert pkgb_dist.version == "0.0.0"
    assert [r.name for r in pkgb_dist.requires] == ["pkga"]
    assert repr(pkgb_dist.requires_dist) == repr([Requirement("pkga<0.0.1")])
    # assert pkga_dist.direct_url is None


@pytest.mark.parametrize(
    "pip_list_function", (_pip_list__env_info_json, _pip_list__pip_inspect, pip_list)
)
def test_pip_list_extras(virtualenv_python, testpkgs, pip_list_function):
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "-f",
            testpkgs,
            "pkge",
        ]
    )
    installed_dists = pip_list_function(virtualenv_python)
    assert set(installed_dists.keys()) == {
        "pkga",
        "pkgb",
        "pkgc",
        "pkgd",
        "pkge",
        "pip",
        "wheel",
        "setuptools",
    }
    pkgd_dist = installed_dists["pkgd"]
    assert repr(pkgd_dist.requires) == repr([Requirement("pkga")])
    assert len(pkgd_dist.extra_requires) == 2
    assert [r.name for r in pkgd_dist.extra_requires["b"]] == ["pkgb"]
    assert [r.name for r in pkgd_dist.extra_requires["c"]] == ["pkgc"]
    pkge_dist = installed_dists["pkge"]
    assert repr(pkge_dist.requires) == repr([Requirement("pkgd[b,c]")])
