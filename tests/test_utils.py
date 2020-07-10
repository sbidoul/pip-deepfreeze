import pytest

from pip_deepfreeze.utils import split_lines


@pytest.mark.parametrize(
    "s, expected",
    [("", []), ("l1", ["l1"]), ("l1\nl2", ["l1", "l2"]), ("\nl1\nl2\n", ["l1", "l2"])],
)
def test_split_lines(s, expected):
    assert split_lines(s) == expected
