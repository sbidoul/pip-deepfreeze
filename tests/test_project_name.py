import sys
import textwrap

from pip_deepfreeze.project_name import get_project_name


def test_project_name_setup_py(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        textwrap.dedent(
            """
            from setuptools import setup

            setup(name="foobar", version="0.0.1")
            """
        )
    )
    assert get_project_name(sys.executable, tmp_path) == "foobar"


def test_project_name_flit(tmp_path):
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
    assert get_project_name(sys.executable, tmp_path) == "foobar"
