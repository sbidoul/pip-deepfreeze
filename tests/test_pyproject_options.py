import textwrap
from pathlib import Path
from unittest.mock import create_autospec

from pytest import MonkeyPatch
from typer.testing import CliRunner

from pip_deepfreeze.__main__ import MainOptions, app
from pip_deepfreeze.sync import sync


def test_options_loaded_from_pyproject_toml_project_root(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Test that options are loaded from pyproject.toml, when --project-root is used."""
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "test"
            version = "1.0"

            [tool.pip-deepfreeze.sync]
            extras = "a,b"
            post_sync_commands = ["echo a", "echo b"]
            """
        )
    )
    sync_operation_mock = create_autospec(sync)
    monkeypatch.setattr("pip_deepfreeze.__main__.sync_operation", sync_operation_mock)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, ["-r", str(tmp_path), "sync"], obj=MainOptions())
    assert result.exit_code == 0
    assert sync_operation_mock.call_args.kwargs["extras"] == ["a", "b"]
    assert sync_operation_mock.call_args.kwargs["post_sync_commands"] == [
        "echo a",
        "echo b",
    ]


def test_options_loaded_from_pyproject_toml_cwd(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Test that options are loaded from pyproject.toml in cwd."""
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "test"
            version = "1.0"

            [tool.pip-deepfreeze.sync]
            extras = "a,b"
            post_sync_commands = ["echo a", "echo b"]
            """
        )
    )
    sync_operation_mock = create_autospec(sync)
    monkeypatch.setattr("pip_deepfreeze.__main__.sync_operation", sync_operation_mock)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, ["sync"], obj=MainOptions())
    assert result.exit_code == 0
    assert sync_operation_mock.call_args.kwargs["extras"] == ["a", "b"]
    assert sync_operation_mock.call_args.kwargs["post_sync_commands"] == [
        "echo a",
        "echo b",
    ]
