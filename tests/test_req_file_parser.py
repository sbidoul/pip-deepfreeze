import os
import textwrap

import pytest

from pip_deepfreeze.req_file_parser import (
    OptionParsingError,
    RequirementLine,
    RequirementsFileParserError,
    _file_or_url_join,
    parse,
    parse_lines,
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
    assert lines[0].raw_line == "req1"
    assert lines[0].lineno == 2


def test_parse_lines(tmp_path):
    """Basic test for parse_lines."""
    lines = ["req1\n", "-r subreqs.txt\n"]
    (tmp_path / "subreqs.txt").write_text("req2")
    parsed_lines = list(parse_lines(lines, filename=str(tmp_path / "req.txt")))
    assert [line.requirement for line in parsed_lines] == ["req1", "req2"]
    assert parsed_lines[0].raw_line == "req1"
    assert parsed_lines[0].lineno == 1


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
            f"""\
            req1
            -r {subreqs_uri}
            """
        )
    )
    subreqs.write_text("req2")
    lines = list(parse(str(reqs)))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]
    lines = list(parse(str(reqs), recurse=False))
    assert [line.requirement for line in lines] == ["req1"]


def test_file_url_not_found(tmp_path):
    reqs = tmp_path / "reqs.txt"
    subreqs_uri = (tmp_path / "notfound.txt").as_uri()
    assert subreqs_uri.startswith("file://")
    reqs.write_text(f"--requirements {subreqs_uri}")
    with pytest.raises(RequirementsFileParserError) as e:
        list(parse(str(reqs)))
    assert "Could not open requirements file" in str(e.value)
    assert "notfound.txt" in str(e.value)


class MockHttpResponse:
    def __init__(self, url, text):
        self.url = url
        self.text = text

    def raise_for_status(self):
        if self.text is None:
            raise RuntimeError(f"mock error opening {self.url}")


class MockHttpFetcher:
    def __init__(self, url, text):
        self.url = url
        self.text = text

    def __call__(self, url):
        if self.text is None:
            raise RuntimeError(f"could not open {self.url}")
        assert url == self.url
        return self.text


def test_http_url(tmp_path):
    subreqs_url = "http://e.c/subreqs.txt"

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
    assert f"Cannot get {subreqs_url} because no http fetcher is available" in str(
        e.value
    )
    lines = list(parse(str(reqs), http_fetcher=MockHttpFetcher(subreqs_url, "req2")))
    assert all(isinstance(line, RequirementLine) for line in lines)
    assert [line.requirement for line in lines] == ["req1", "req2"]
    lines = list(parse(str(reqs), recurse=False))
    assert [line.requirement for line in lines] == ["req1"]


def test_http_url_notfound(tmp_path):
    subreqs_url = "http://e.c/notfound.txt"
    reqs = tmp_path / "reqs.txt"
    reqs.write_text(f"-r {subreqs_url}")
    with pytest.raises(RequirementsFileParserError) as e:
        list(parse(str(reqs), http_fetcher=MockHttpFetcher(subreqs_url, None)))
    assert "Could not open requirements file" in str(e.value)
    assert "notfound.txt" in str(e.value)


def test_subreq_notfound(tmp_path):
    reqs = tmp_path / "reqs.txt"
    reqs.write_text("-r notfound.txt")
    with pytest.raises(RequirementsFileParserError) as e:
        _ = list(parse(str(reqs)))
    assert "Could not open requirements file" in str(e.value)
    assert "notfound.txt" in str(e.value)


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
            f"""\
            req1
            -r {subreqs_uri}
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
    "badreqs", ["-r", "--requirements", "-c", "--constraints", "-e", "--editable"]
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


@pytest.mark.parametrize(
    "filename,base_filename,expected",
    [
        ("sr.txt", "r.txt", "sr.txt"),
        ("sr.txt", None, "sr.txt"),
        ("sr.txt", "a/r.txt", f"a{os.path.sep}sr.txt"),
        ("b/sr.txt", "a/r.txt", f"a{os.path.sep}b/sr.txt"),
        ("file:///a/sr.txt", None, "file:///a/sr.txt"),
        ("file:///a/sr.txt", "r.txt", "file:///a/sr.txt"),
        ("file:///a/sr.txt", "file:///b/r.txt", "file:///a/sr.txt"),
        ("../sr.txt", "file:///b/r.txt", "file:///sr.txt"),
    ],
)
def test_file_or_url_join(filename, base_filename, expected):
    assert _file_or_url_join(filename, base_filename) == expected


# TODO test constraints and nested constraints
# TODO test auto-decode
