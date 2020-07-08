import pytest

from pip_deepfreeze.req_parser import canonicalize_name, get_req_name


@pytest.mark.parametrize(
    "req_name,expected",
    [("pkga", "pkga"), ("PkgA", "pkga"), ("PkgA.b-c__d", "pkga-b-c-d")],
)
def test_canonicalize_name(req_name, expected):
    assert canonicalize_name(req_name) == expected


@pytest.mark.parametrize(
    "requirement,expected",
    [
        ("pkga", "pkga"),
        ("PkgA", "pkga"),
        ("pkga @ https://e.c/pkga.tgz", "pkga"),
        ("./pkga.tgz", None),
    ],
)
def test_get_req_name(requirement, expected):
    assert get_req_name(requirement) == expected
