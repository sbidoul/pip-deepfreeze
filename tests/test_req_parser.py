import pytest

from pip_deepfreeze.req_parser import get_req_name, get_req_names


@pytest.mark.parametrize(
    "requirement,expected",
    [
        ("pkga", "pkga"),
        ("PkgA", "pkga"),
        ("pkga @ https://e.c/pkga.tgz", "pkga"),
        ("./pkga.tgz", None),
        ("git+https://g.c/o/r@1.0#egg=Pkga&subdirectory=python", "pkga"),
        ("git+https://g.c/o/r@1.0#egg=P&subdirectory=python", "p"),
        ("git+https://g.c/o/r@1.0#egg=P.&subdirectory=python", None),
        ("git+https://g.c/o/r@1.0#egg=P", "p"),
        ("git+https://g.c/o/r@1.0#egg=P.a", "p-a"),
    ],
)
def test_get_req_name(requirement, expected):
    assert get_req_name(requirement) == expected


@pytest.mark.parametrize(
    "requirements,expected", [(["pkga", "./pkga", "pkgb"], ["pkga", "pkgb"])]
)
def test_get_req_names(requirements, expected):
    assert get_req_names(requirements) == expected
