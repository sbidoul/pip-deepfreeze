import subprocess

from typer.testing import CliRunner

from pip_deepfreeze.__main__ import app
from pip_deepfreeze.sanity import check_env


def test_sanity_pip(virtualenv_python, capsys):
    assert check_env(virtualenv_python)
    subprocess.check_call([virtualenv_python, "-m", "pip", "uninstall", "-y", "pip"])
    assert not check_env(virtualenv_python)
    captured = capsys.readouterr()
    assert "pip is not available" in captured.err


def test_sanity_pip_version(virtualenv_python, capsys):
    assert check_env(virtualenv_python)
    subprocess.check_call([virtualenv_python, "-m", "pip", "install", "-q", "pip<20.1"])
    assert check_env(virtualenv_python)
    captured = capsys.readouterr()
    assert "works best with pip>=20.1" in captured.err


def test_sanity_pkg_resources(virtualenv_python, capsys):
    assert check_env(virtualenv_python)
    subprocess.check_call(
        [virtualenv_python, "-m", "pip", "uninstall", "-qy", "setuptools"]
    )
    # pkg_resources is currently required
    assert not check_env(virtualenv_python)
    captured = capsys.readouterr()
    assert "pkg_resources is not available" in captured.err


def test_sanity_wheel(virtualenv_python, capsys):
    assert check_env(virtualenv_python)
    subprocess.check_call([virtualenv_python, "-m", "pip", "uninstall", "-qy", "wheel"])
    # wheel is not strictly required, although pip works better with it
    assert check_env(virtualenv_python)
    captured = capsys.readouterr()
    assert "wheel is not available" in captured.err


def test_sanity_main(virtualenv_python):
    subprocess.check_call([virtualenv_python, "-m", "pip", "uninstall", "-qy", "pip"])
    runner = CliRunner()
    result = runner.invoke(app, ["--python", virtualenv_python, "tree"])
    assert result.exit_code != 0
    assert "pip not available", result.stderr
