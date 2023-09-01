import subprocess
import textwrap

from typer.testing import CliRunner

from pip_deepfreeze.__main__ import MainOptions, app


def test_tree(virtualenv_python, testpkgs, tmp_path):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(name="theproject", install_requires=["pkge"])
            """
        )
    )
    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "-f",
            testpkgs,
            tmp_path,
        ]
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        app,
        ["-p", virtualenv_python, "-r", tmp_path, "tree"],
        obj=MainOptions(),
    )
    assert result.exit_code == 0
    assert result.stdout == textwrap.dedent(
        f"""\
        theproject (0.0.0 @ {tmp_path.as_uri()})
        └── pkge (0.0.0)
            └── pkgd[b,c] (0.0.0)
                ├── pkga (0.0.0)
                ├── pkgb (0.0.0)
                │   └── pkga ⬆
                └── pkgc (0.0.2)
        """
    )


def test_tree_extras(virtualenv_python, testpkgs, tmp_path):
    (tmp_path / "setup.py").write_text(
        textwrap.dedent(
            """\
            from setuptools import setup

            setup(
                name="theproject",
                install_requires=["pkga"],
                extras_require={"c": ["pkgd[c]"]},
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
            "--no-index",
            "-f",
            testpkgs,
            str(tmp_path) + "[c]",
        ]
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        app,
        ["-p", virtualenv_python, "-r", tmp_path, "tree", "-x", "c"],
        obj=MainOptions(),
    )
    assert result.exit_code == 0
    assert result.stdout == textwrap.dedent(
        f"""\
        theproject[c] (0.0.0 @ {tmp_path.as_uri()})
        ├── pkga (0.0.0)
        └── pkgd[c] (0.0.0)
            ├── pkga ⬆
            └── pkgc (0.0.2)
        """
    )
