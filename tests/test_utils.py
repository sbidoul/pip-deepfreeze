import sys

import pytest
import typer

from pip_deepfreeze.utils import (
    check_call,
    check_output,
    log_error,
    log_info,
    log_warning,
    open_with_rollback,
    split_lines,
)


@pytest.mark.parametrize(
    "s, expected",
    [("", []), ("l1", ["l1"]), ("l1\nl2", ["l1", "l2"]), ("\nl1\nl2\n", ["l1", "l2"])],
)
def test_split_lines(s, expected):
    assert split_lines(s) == expected


def test_open_with_rollback(tmp_path):
    filename = tmp_path / "thefile"
    with open_with_rollback(filename) as f:
        f.write("a")
    assert filename.exists()
    assert filename.read_text() == "a"
    try:
        with open_with_rollback(filename) as f:
            f.write("b")
            raise RuntimeError
    except RuntimeError:
        assert filename.read_text() == "a"
    else:
        raise AssertionError("should not be here")


def test_log_info(capsys):
    log_info("in", nl=False)
    log_info("fo")
    assert capsys.readouterr().err == "info\n"


def test_log_warning(capsys):
    log_warning("warning")
    assert capsys.readouterr().err == "warning\n"


def test_log_error(capsys):
    log_error("error")
    assert capsys.readouterr().err == "error\n"


def test_check_call(capsys):
    r = check_call([sys.executable, "-c", "print('toto')"])
    assert r == 0
    with pytest.raises(typer.Exit) as e:
        check_call([sys.executable, "-c", "import sys; sys.exit(1)"])
    assert e.value.exit_code == 1
    "Error running: " in capsys.readouterr().err


def test_check_output(capsys):
    r = check_output([sys.executable, "-c", "print('toto')"])
    assert r == "toto\n"
    with pytest.raises(typer.Exit) as e:
        check_output([sys.executable, "-c", "import sys; sys.exit(1)"])
    assert e.value.exit_code == 1
    "Error running: " in capsys.readouterr().err
