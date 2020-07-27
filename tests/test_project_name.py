import sys
import textwrap

from pip_deepfreeze.project_name import (
    _load_pyproject_toml,
    get_project_name,
    get_project_name_from_pep517,
    get_project_name_from_pyproject_toml_flit,
    get_project_name_from_pyproject_toml_pep621,
    get_project_name_from_setup_cfg,
)


def test_project_name_from_setup_cfg(tmp_path):
    (tmp_path / "setup.cfg").write_text("[metadata]\nname = theproject")
    assert (
        get_project_name_from_setup_cfg(tmp_path, _load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"
    (tmp_path / "pyproject.toml").touch()
    assert (
        get_project_name_from_setup_cfg(tmp_path, _load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"
    (tmp_path / "pyproject.toml").write_text("[build-system]")
    assert (
        get_project_name_from_setup_cfg(tmp_path, _load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"
    (tmp_path / "pyproject.toml").write_text(
        '[build-system]\nbuild-backend="setuptools.build_meta"'
    )
    assert (
        get_project_name_from_setup_cfg(tmp_path, _load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"
    (tmp_path / "setup.cfg").write_text("[metadata]")
    assert not get_project_name_from_setup_cfg(tmp_path, _load_pyproject_toml(tmp_path))


def test_get_project_name_from_pyproject_toml_flit(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """\
            [build-system]
            build-backend = "flit_core.buildapi"

            [tool.flit.metadata]
            module = "theproject"
            """
        )
    )
    assert (
        get_project_name_from_pyproject_toml_flit(_load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"


def test_get_project_name_from_pyproject_toml_pep621(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """\
            [build-system]
            build-backend = "abackend"

            [project]
            name = "theproject"
            """
        )
    )
    assert (
        get_project_name_from_pyproject_toml_pep621(_load_pyproject_toml(tmp_path))
        == "theproject"
    )
    assert get_project_name(sys.executable, tmp_path) == "theproject"


def test_project_name_from_pep517_setup_py(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(name="foobar", version="0.0.1")
            """
        )
    )
    assert get_project_name_from_pep517(sys.executable, tmp_path) == "foobar"
    assert get_project_name(sys.executable, tmp_path) == "foobar"


def test_project_name_from_pep517_flit(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [build-system]
            requires = ["flit_core >=2,<4"]
            build-backend = "flit_core.buildapi"

            [tool.flit.metadata]
            module = "foobar"
            author = "Toto"
            """
        )
    )
    (tmp_path / "foobar.py").write_text(
        textwrap.dedent(
            """
            '''This is foobar'''
            __version__ = '0.0.1'
            """
        )
    )
    assert get_project_name_from_pep517(sys.executable, tmp_path) == "foobar"
    assert get_project_name(sys.executable, tmp_path) == "foobar"
