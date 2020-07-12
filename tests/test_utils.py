import pytest

from pip_deepfreeze.utils import open_with_rollback, split_lines


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
