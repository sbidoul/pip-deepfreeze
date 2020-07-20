import textwrap

import pytest

from pip_deepfreeze.req_file_parser import (
    OptionParsingError,
    RequirementLine,
    RequirementsFileParserError,
    parse,
)


def test_basic(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            # comment
            req1
            req2==1.0.0
            req3 @ https://e.c/req3.tgz
            ./req4
            https://e.c/req5.tgz
            req6 @ https://e.c/req6.tgz ; python_version < 3.7  # comment
            req6 ; python_version >= 3.7  # released version is ok
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == [
        "req1",
        "req2==1.0.0",
        "req3 @ https://e.c/req3.tgz",
        "./req4",
        "https://e.c/req5.tgz",
        "req6 @ https://e.c/req6.tgz ; python_version < 3.7",
        "req6 ; python_version >= 3.7",
    ]


def test_recurse(tmp_path):
    reqs = tmp_path / "reqs.txt"
    subreqs = tmp_path / "subreqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            req1
            -r subreqs.txt
            """
        )
    )
    subreqs.write_text("req2")
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]
    lines = list(parse(str(reqs), recurse=False))
    assert [line.requirement for line in lines] == ["req1"]


def test_file_url(tmp_path):
    reqs = tmp_path / "reqs.txt"
    subreqs = tmp_path / "subreqs.txt"
    subreqs_uri = subreqs.as_uri()
    assert subreqs_uri.startswith("file://")
    reqs.write_text(
        textwrap.dedent(
            """\
            req1
            -r {}
            """.format(
                subreqs_uri
            )
        )
    )
    subreqs.write_text("req2")
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]
    lines = list(parse(str(reqs), recurse=False))
    assert [line.requirement for line in lines] == ["req1"]


def test_http_url(tmp_path):
    subreqs_url = "http://e.c/subreqs.txt"

    class MockHttpResponse:
        text = "req2"

        def raise_for_status(self):
            pass

    class MockHttpSession:
        def get(self, url):
            assert url == subreqs_url
            return MockHttpResponse()

    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            f"""\
            req1
            -r {subreqs_url}
            """
        )
    )
    with pytest.raises(RequirementsFileParserError) as e:
        list(parse(str(reqs)))
    assert f"Cannot get {subreqs_url} because no http session is available" in str(
        e.value
    )
    lines = list(parse(str(reqs), session=MockHttpSession()))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]
    lines = list(parse(str(reqs), recurse=False))
    assert [line.requirement for line in lines] == ["req1"]


def test_subreq_notfound(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text("-r notfound.txt")
    with pytest.raises(RequirementsFileParserError):
        _ = list(parse(str(reqs)))


def test_relative_file(tmp_path):
    reqs = tmp_path / "reqs.txt"
    (tmp_path / "subdir").mkdir()
    subreqs = tmp_path / "subdir" / "subreqs.txt"
    subsubreqs = tmp_path / "subdir" / "subsubreqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            req1
            -r subdir/subreqs.txt
            """
        )
    )
    subreqs.write_text(
        textwrap.dedent(
            """\
            req2
            -r ./subsubreqs.txt
            """
        )
    )
    subsubreqs.write_text("req3")
    lines = list(parse(str(reqs)))
    assert [line.requirement for line in lines] == ["req1", "req2", "req3"]


def test_relative_file_uri(tmp_path):
    reqs = tmp_path / "reqs.txt"
    (tmp_path / "subdir").mkdir()
    subreqs = tmp_path / "subdir" / "subreqs.txt"
    subreqs_uri = subreqs.as_uri()
    assert subreqs_uri.startswith("file://")
    subsubreqs = tmp_path / "subdir" / "subsubreqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            req1
            -r {}
            """.format(
                subreqs_uri
            )
        )
    )
    subreqs.write_text(
        textwrap.dedent(
            """\
            req2
            -r ./subsubreqs.txt
            """
        )
    )
    subsubreqs.write_text("req3")
    lines = list(parse(str(reqs)))
    assert [line.requirement for line in lines] == ["req1", "req2", "req3"]


def test_editable(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            # comment
            req1
            -e ./req2  # comment
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "./req2"]
    assert [line.is_editable for line in lines] == [False, True]


def test_multiline_req(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            req @ \\
            ./req.tgz  # comment
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert [line.requirement for line in lines] == ["req @ ./req.tgz"]


@pytest.mark.xfail(reason="hash parsing not implemented")
def test_hashes(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            req @ ./req.tgz \\
                --hash sha1:62bd26d758...703a094285 \\
                --hash sha2:xyz
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert [line.requirement for line in lines] == ["req @ ./req.tgz"]
    assert lines[0].options["hashes"] == ["sha1:62bd26d758...703a094285", "sha2:xyz"]


def test_last_line_continuation(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            # comment
            req1
            req2\\
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]


def test_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("X_USER", "toto")
    monkeypatch.setenv("X_PASSWORD", "lehéro")
    monkeypatch.setenv("Z_USER", "")
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(
        textwrap.dedent(
            """\
            https://${X_USER}@e.c/req.tgz
            https://${X_USER}:${X_PASSWORD}@e.c/req.tgz
            https://${Y_USER}@e.c/req.tgz
            https://${Z_USER}@e.c/req.tgz
            """
        )
    )
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == [
        "https://toto@e.c/req.tgz",
        "https://toto:lehéro@e.c/req.tgz",
        "https://${Y_USER}@e.c/req.tgz",
        "https://@e.c/req.tgz",
    ]


@pytest.mark.parametrize(
    "badreqs",
    [
        "-e ./req1 -e ./req2",
        "-r f1 -e ./req1",
        "-r f1 -r f2",
        "-c c1 -c c2",
        "-r f1 -c c1",
        "-r f1 --hash x",
        "-r f1 -f z",
        "-e ./req1 --hash x",  # editable can't have options
    ],
)
def test_strict_option_errors(badreqs, tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(badreqs)
    _ = list(parse(str(reqs), recurse=False, strict=False))
    with pytest.raises(OptionParsingError):
        _ = list(parse(str(reqs), recurse=False, strict=True))


@pytest.mark.parametrize(
    "badreqs", ["-r", "--requirements", "-c", "--constraints", "-e", "--editable"],
)
def test_option_errors(badreqs, tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(badreqs)
    with pytest.raises(OptionParsingError):
        _ = list(parse(str(reqs), recurse=False))


@pytest.mark.parametrize(
    "line, expected",
    [
        ("-i https://e.c/simple", ["-i", "https://e.c/simple"]),
        (
            "--extra-index-url https://a.u/simple",
            ["--extra-index-url", "https://a.u/simple"],
        ),
        (
            "--find-links https://x.y/links   -f ./links",
            ["--find-links", "https://x.y/links", "-f", "./links"],
        ),
        ("-f ./otherlinks", ["-f", "./otherlinks"]),
        ('-f "dir with space/subdir"', ["-f", "dir with space/subdir"]),
        ("--pre", ["--pre"]),
        ("pkga --hash h:v --hash x:y", ["--hash", "h:v", "--hash", "x:y"]),
        ("pkgb ; python_version<3.7 --hash h:v", ["--hash", "h:v"]),
        ("--editable=./pkg", []),
        ("-e ./pkg", []),
        ("foo==1.0", []),
    ],
)
def test_options(line, expected, tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(line)
    lines = list(parse(str(reqs), reqs_only=False, recurse=False))
    assert len(lines) == 1
    assert lines[0].options == expected


# TODO test constraints and nested constraints
# TODO test req_only=False
# TODO test parse with base_filename
# TODO test auto-decode
