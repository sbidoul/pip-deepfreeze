import sys

import pytest
import typer

from pip_deepfreeze.utils import (
    check_call,
    check_output,
    comma_split,
    decrease_verbosity,
    increase_verbosity,
    log_debug,
    log_error,
    log_info,
    log_notice,
    log_warning,
    make_project_name_with_extras,
    normalize_req_line,
    open_with_rollback,
)


def test_open_with_rollback(tmp_path):
    filename = tmp_path / "thefile"
    # file does not exist
    with open_with_rollback(filename) as f:
        f.write("a")
    assert filename.exists()
    assert filename.read_text() == "a"
    # file exists
    with open_with_rollback(filename) as f:
        f.write("b")
    assert filename.exists()
    assert filename.read_text() == "b"
    # error while writing -> rollback
    try:
        with open_with_rollback(filename) as f:
            f.write("c")
            raise RuntimeError
    except RuntimeError:
        assert filename.read_text() == "b"
    else:
        raise AssertionError("should not be here")


def test_open_with_rollback_logging(tmp_path, capsys):
    filename = tmp_path / "thefile"
    with open_with_rollback(filename) as f:
        f.write("a")
    assert capsys.readouterr().err == f"Created {filename}\n"
    with open_with_rollback(filename) as f:
        f.write("a")
    assert capsys.readouterr().err == f"No change to {filename}\n"
    with open_with_rollback(filename) as f:
        f.write("b")
    assert capsys.readouterr().err == f"Updated {filename}\n"


def test_log_debug(capsys):
    log_debug("debug")
    assert "debug" not in capsys.readouterr().err
    increase_verbosity()
    try:
        log_debug("debug")
        assert capsys.readouterr().err == "debug\n"
    finally:
        decrease_verbosity()


def test_log_info(capsys):
    log_info("in", nl=False)
    log_info("fo")
    assert capsys.readouterr().err == "info\n"


def test_log_notice(capsys):
    log_notice("in", nl=False)
    log_notice("fo")
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
    assert "Error running: " in capsys.readouterr().err


def test_check_output(capsys):
    r = check_output([sys.executable, "-c", "print('toto')"])
    assert r == "toto\n"
    with pytest.raises(typer.Exit) as e:
        check_output([sys.executable, "-c", "import sys; sys.exit(1)"])
    assert e.value.exit_code == 1
    assert "Error running: " in capsys.readouterr().err


@pytest.mark.parametrize(
    "s, expected",
    [
        (None, []),
        ("", []),
        ("  ", []),
        (" a", ["a"]),
        ("a, b", ["a", "b"]),
        ("a,,b, c ", ["a", "b", "c"]),
    ],
)
def test_comma_split(s, expected):
    assert comma_split(s) == expected


@pytest.mark.parametrize(
    "project_name, extras, expected",
    [
        ("prj", None, "prj"),
        ("prj", [], "prj"),
        ("prj", ["e1"], "prj[e1]"),
        ("prj", ["e1", "e2"], "prj[e1,e2]"),
    ],
)
def test_make_project_name_with_extras(project_name, extras, expected):
    assert make_project_name_with_extras(project_name, extras) == expected


@pytest.mark.parametrize(
    "req_line, expected",
    [
        ("prj", "prj"),
        ("prj==1.0", "prj==1.0"),
        ("name @https://g.c/o/p@branch", "name @ https://g.c/o/p@branch"),
        ("name@https://g.c/o/p@branch", "name @ https://g.c/o/p@branch"),
        ("name[extra] @https://g.c/o/p@branch", "name[extra] @ https://g.c/o/p@branch"),
    ],
)
def test_normalize_req_line(req_line: str, expected: str) -> None:
    assert normalize_req_line(req_line) == expected
