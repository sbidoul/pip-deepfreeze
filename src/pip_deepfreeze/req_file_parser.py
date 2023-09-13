"""Requirements file parsing.

This comes from pip.

Notes about changes made compared to the pip source code, with the goal of
moving this to a standalone library:

- empty environment variables are replaced (TODO in pip, see
  https://github.com/pypa/pip/issues/8422)
- nested constraints?
"""

# TODO better name than filename/base_filename

from __future__ import absolute_import

import argparse
import codecs
import locale
import os
import re
import shlex
import sys
from typing import Callable, Iterable, Iterator, List, NoReturn, Optional, Text, Tuple, Union
from urllib import parse as urllib_parse
from urllib.request import urlopen

ReqFileLines = Iterator[Tuple[int, Text, Text]]


__all__ = [
    "parse",
    "parse_lines",
    "RequirementsFileParserError",
    "OptionParsingError",
    "ParsedLine",
    "RequirementLine",
    "NestedRequirementsLine",
    "OptionsLine",
]

_SCHEME_RE = re.compile(r"^(http|https|file):", re.I)
_COMMENT_RE = re.compile(r"(^|\s+)#.*$")
_URL_SLASH_DRIVE_RE = re.compile(r"/*([a-z])\|", re.I)
# Matches environment variable-style values in '${MY_VARIABLE_1}' with the
# variable name consisting of only uppercase letters, digits or the '_'
# (underscore). This follows the POSIX standard defined in IEEE Std 1003.1,
# 2013 Edition.
_ENV_VAR_RE = re.compile(r"(?P<var>\$\{(?P<name>[A-Z0-9_]+)\})")


HttpFetcher = Callable[[str], str]

class RequirementsFileParserError(Exception):
    pass


class OptionParsingError(RequirementsFileParserError):
    def __init__(self, msg, filename, lineno):
        # type: (str, str, int) -> None
        super().__init__(
            "{msg} at {filename}:{lineno}".format(
                msg=msg, filename=filename, lineno=lineno
            )
        )


class ParsedLine(object):
    def __init__(
        self,
        filename,  # type: str
        lineno,  # type: int
        raw_line,  # type: str
    ):
        self.filename = filename
        self.lineno = lineno
        self.raw_line = raw_line


class RequirementLine(ParsedLine):
    def __init__(
        self,
        filename,  # type: str
        lineno,  # type: int
        raw_line,  # type: str
        requirement,  # type: str
        is_editable,  # type: bool
        is_constraint,  # type: bool
        options,  # type: List[str]
    ):
        super().__init__(filename, lineno, raw_line)
        self.requirement = requirement
        self.is_editable = is_editable
        self.is_constraint = is_constraint
        self.options = options


class NestedRequirementsLine(ParsedLine):
    def __init__(
        self,
        filename,  # type: str
        lineno,  # type: int
        raw_line,  # type: str
        requirements,  # type: str
        is_constraint,  # type: bool
    ):
        super().__init__(filename, lineno, raw_line)
        self.requirements = requirements
        self.is_constraint = is_constraint


class OptionsLine(ParsedLine):
    def __init__(
        self,
        filename,  # type: str
        lineno,  # type: int
        raw_line,  # type: str
        options,  # type: List[str]
    ):
        super().__init__(filename, lineno, raw_line)
        self.options = options


def _preprocess_lines(lines):
    # type: (Iterable[str]) -> ReqFileLines
    """Split, filter, and join lines, and return a line iterator."""
    lines_enum = _join_lines(enumerate(lines, start=1))
    lines_enum = _remove_comments(lines_enum)
    lines_enum = _expand_env_variables(lines_enum)
    return lines_enum


def parse(
    filename,  # type: str
    recurse=True,  # type: bool
    reqs_only=True,  # type: bool
    strict=False,  # type: bool
    constraints=False,  # type: bool
    http_fetcher=None,  # type: Optional[HttpFetcher]
):
    # type: (...) -> Iterator[ParsedLine]
    return _parse(
        _get_file_lines(filename, http_fetcher),
        filename,
        recurse=recurse,
        reqs_only=reqs_only,
        strict=strict,
        constraints=constraints,
        http_fetcher=http_fetcher,
    )


def parse_lines(
    lines,  # type: Iterable[str]
    filename,  # type: str
    recurse=True,  # type: bool
    reqs_only=True,  # type: bool
    strict=False,  # type: bool
    constraints=False,  # type: bool
    http_fetcher=None,  # type: Optional[HttpFetcher]
):
    # type: (...) -> Iterator[ParsedLine]
    return _parse(
        lines,
        filename,
        recurse=recurse,
        reqs_only=reqs_only,
        strict=strict,
        constraints=constraints,
        http_fetcher=http_fetcher,
    )


def _parse(
    lines,  # type: Iterable[str]
    filename,  # type: str
    recurse=True,  # type: bool
    reqs_only=True,  # type: bool
    strict=False,  # type: bool
    constraints=False,  # type: bool
    http_fetcher=None,  # type: Optional[HttpFetcher]
):
    # type: (...) -> Iterator[ParsedLine]
    """Parse a given file or URL, yielding parsed lines."""
    for line in _parse_lines(lines, filename, constraints, strict):
        if not reqs_only or isinstance(line, RequirementLine):
            yield line
        if isinstance(line, NestedRequirementsLine) and recurse:
            for inner_line in parse(
                filename=_file_or_url_join(line.requirements, line.filename),
                recurse=recurse,
                reqs_only=reqs_only,
                strict=strict,
                constraints=line.is_constraint,
                http_fetcher=http_fetcher,
            ):
                yield inner_line


def _file_or_url_join(filename: str, base_filename: Optional[str]) -> str:
    if not base_filename:
        return filename
    # original file is over http
    if _SCHEME_RE.search(base_filename):
        # do a url join so relative paths work
        return urllib_parse.urljoin(base_filename, filename)
    # original file and nested file are paths
    elif not _SCHEME_RE.search(filename):
        # do a join so relative paths work
        return os.path.join(os.path.dirname(base_filename), filename)
    return filename


def _parse_lines(
    lines,  # type: Iterable[str]
    filename,  # type: str
    constraints,  # type: bool
    strict,  # type: bool
):
    # type: (...) -> Iterator[ParsedLine]
    for lineno, line, raw_line in _preprocess_lines(lines):
        args_str, opts, other_opts = _parse_line(line, filename, lineno, strict)
        if args_str:
            yield RequirementLine(
                filename,
                lineno,
                raw_line,
                requirement=args_str,
                is_editable=False,
                is_constraint=constraints,
                options=other_opts,
            )
        elif opts.editables:
            yield RequirementLine(
                filename,
                lineno,
                raw_line,
                requirement=opts.editables[0],
                is_editable=True,
                is_constraint=constraints,
                options=[],  # XXX can't editables have options?
            )
        elif opts.requirements:
            yield NestedRequirementsLine(
                filename,
                lineno,
                raw_line,
                requirements=opts.requirements[0],
                # XXX this could be `constraints` instead of False
                #     https://github.com/pypa/pip/issues/8416
                is_constraint=False,
            )
        elif opts.constraints:
            yield NestedRequirementsLine(
                filename,
                lineno,
                raw_line,
                requirements=opts.constraints[0],
                is_constraint=True,
            )
        elif other_opts:
            yield OptionsLine(
                filename,
                lineno,
                raw_line,
                options=other_opts,
            )
        else:
            yield ParsedLine(filename, lineno, raw_line)


class ParsedOptions(argparse.Namespace):
    def __init__(self):
        # type: () -> None
        self.editables = []  # type: List[str]
        self.requirements = []  # type: List[str]
        self.constraints = []  # type: List[str]


class ErrorCatchingArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        # type: (int, Optional[str]) -> NoReturn
        raise RequirementsFileParserError(message)


_options_parser = ErrorCatchingArgumentParser()
_options_parser.add_argument("-e", "--editable", action="append", dest="editables")
_options_parser.add_argument("-r", "--requirements", action="append")
_options_parser.add_argument("-c", "--constraints", action="append")


def _parse_line(line, filename, lineno, strict):
    # type: (Text, str, int, bool) -> Tuple[str, ParsedOptions, List[str]]
    args_str, options_str = _break_args_options(line)
    try:
        opts, other_opts = _options_parser.parse_known_args(
            shlex.split(options_str), namespace=ParsedOptions()
        )
    except RequirementsFileParserError as e:
        raise OptionParsingError(str(e), filename, lineno)
    c = len(opts.editables) + len(opts.requirements) + len(opts.constraints)
    if strict and c > 1:
        raise OptionParsingError(
            "Cannot have more than one -e/-c/-r on the same line", filename, lineno
        )
    if strict and c > 0 and other_opts:
        raise OptionParsingError(
            "Cannot mix -e/-c/-r with other options on the same line",
            filename,
            lineno,
        )
    assert isinstance(opts, ParsedOptions)
    return args_str.strip(), opts, other_opts


def _break_args_options(line):
    # type: (Text) -> Tuple[str, Text]
    """Break up the line into an args and options string.

    We only want to shlex (and then optparse) the options, not the args.
    args can contain markers which are corrupted by shlex.
    """
    tokens = line.split(" ")
    args = []
    options = tokens[:]
    for token in tokens:
        if token.startswith("-"):
            break
        else:
            args.append(token)
            options.pop(0)
    return " ".join(args), " ".join(options)


def _join_lines(lines_enum):
    # type: (Iterator[Tuple[int, Text]]) -> ReqFileLines
    """Joins a line ending in '\' with the previous line (except when following
    comments).

    The joined line takes on the index of the first line.
    """
    primary_line_number = None
    new_lines = []  # type: List[Text]
    raw_lines = []  # type: List[Text]
    for line_number, raw_line in lines_enum:
        raw_line = raw_line.rstrip("\n")  # in case lines comes from open()
        if not raw_line.endswith("\\") or _COMMENT_RE.match(raw_line):
            if _COMMENT_RE.match(raw_line):
                # this ensures comments are always matched later
                line = " " + raw_line
            else:
                line = raw_line
            if new_lines:
                new_lines.append(line)
                raw_lines.append(raw_line)
                assert primary_line_number is not None
                yield primary_line_number, "".join(new_lines), "\n".join(raw_lines)
                new_lines = []
                raw_lines = []
            else:
                yield line_number, line, raw_line
        else:
            if not new_lines:
                primary_line_number = line_number
            new_lines.append(raw_line.strip("\\"))
            raw_lines.append(raw_line)

    # last line contains \
    if new_lines:
        assert primary_line_number is not None
        yield primary_line_number, "".join(new_lines), "\n".join(raw_lines)

    # TODO (from pip codebase): handle space after '\'.


def _remove_comments(lines_enum):
    # type: (ReqFileLines) -> ReqFileLines
    """Strips comments and filter empty lines."""
    for line_number, line, raw_line in lines_enum:
        line = _COMMENT_RE.sub("", line)
        line = line.strip()
        yield line_number, line, raw_line


def _expand_env_variables(lines_enum):
    # type: (ReqFileLines) -> ReqFileLines
    """Replace all environment variables that can be retrieved via `os.getenv`.

    The only allowed format for environment variables defined in the
    requirement file is `${MY_VARIABLE_1}` to ensure two things:

    1. Strings that contain a `$` aren't accidentally (partially) expanded.
    2. Ensure consistency across platforms for requirement files.

    These points are the result of a discussion on the `github pull
    request #3514 <https://github.com/pypa/pip/pull/3514>`_.

    Valid characters in variable names follow the `POSIX standard
    <http://pubs.opengroup.org/onlinepubs/9699919799/>`_ and are limited
    to uppercase letter, digits and the `_` (underscore).
    """
    for line_number, line, raw_line in lines_enum:
        for env_var, var_name in _ENV_VAR_RE.findall(line):
            value = os.getenv(var_name)
            if value is None:
                continue

            line = line.replace(env_var, value)

        yield line_number, line, raw_line


_BOMS = [
    (codecs.BOM_UTF8, "utf-8"),
    (codecs.BOM_UTF16, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF32, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF32_LE, "utf-32-le"),
]  # type: List[Tuple[bytes, Text]]

_ENCODING_RE = re.compile(rb"coding[:=]\s*([-\w.]+)")


def _auto_decode(data):
    # type: (bytes) -> Text
    """Check a bytes string for a BOM to correctly detect the encoding.

    Fallback to locale.getpreferredencoding(False) like open() on
    Python3
    """
    for bom, encoding in _BOMS:
        if data.startswith(bom):
            return data[len(bom) :].decode(encoding)
    # Lets check the first two lines as in PEP263
    for line in data.split(b"\n")[:2]:
        if line[0:1] == b"#" and _ENCODING_RE.search(line):
            result = _ENCODING_RE.search(line)
            assert result is not None
            encoding = result.groups()[0].decode("ascii")
            return data.decode(encoding)
    return data.decode(locale.getpreferredencoding(False) or sys.getdefaultencoding())


def _get_url_scheme(url):
    # type: (Union[str, Text]) -> Optional[Text]
    if ":" not in url:
        return None
    return url.split(":", 1)[0].lower()


def _get_file_lines(url, http_fetcher):
    # type: (str, Optional[HttpFetcher]) -> Iterable[str]
    """Gets the content of a file as unicode; it may be a filename, file: URL, or
    http: URL. Respects # -*- coding: declarations on the retrieved files.

    :param url:          File path or url.
    :param http_fetcher: HttpFetcher instance.
    """
    scheme = _get_url_scheme(url)
    if scheme in ["http", "https"]:
        if not http_fetcher:
            # FIXME better exception
            raise RequirementsFileParserError(
                "Cannot get {url} because no http fetcher is available.".format(url=url)
            )
        try:
            content = http_fetcher(url)
        except Exception as exc:
            raise RequirementsFileParserError(
                "Could not open requirements file: {}".format(exc)
            )
    elif scheme == "file":
        try:
            with urlopen(url) as f:
                content = _auto_decode(f.read())
        except Exception as exc:
            raise RequirementsFileParserError(
                "Could not open requirements file: {}".format(exc)
            )
    else:
        try:
            with open(url, "rb") as f:
                content = _auto_decode(f.read())
        except Exception as exc:
            raise RequirementsFileParserError(
                "Could not open requirements file: {}".format(exc)
            )
    return content.splitlines()
