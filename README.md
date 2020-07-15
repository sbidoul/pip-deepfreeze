# pip-deepfreeze

A simple pip freeze workflow for Python application developers.

## About

`pip-deepfreeze` aims at doing one thing and doing it well, namely installing
and pinning dependencies of Python applications (not libraries) in a virtual environment.

- It is easy to use.
- It is fast.
- It is written in Python 3.6+, yet works in any virtual environment that has
  `pip` installed, including python 2.
- It relies on the documented `pip` CLI and requirements file format.
- It is small, simple, with good test coverage and hopefully easy to maintain.

## Installation

Using [pipx](https://pypi.org/project/pipx/) (recommended):

```console
pipx install pip-deepfreeze
```

Using [pip](https://pypi.org/project/pip/):

```console
pip install --user pip-deepfreeze
```

It is *not* recommended to install `pip-deepfreeze` in the same environment as
your application, so its dependencies do not interfere with your app. By
default it works with the `python` found in your `PATH` (which does what you
normally expect in an activated virtualenv), but you can ask it to work within
another environment using the `--python` option.

## Quick start

Make sure your application declares its dependencies using
[setuptools](https://pypi.org/project/setuptools/) (via the `install_requires`
key in `setup.py` or `setup.cfg`), or any other compliant [PEP
517](https://www.python.org/dev/peps/pep-0517/) build backend such as
[flit](https://pypi.org/project/flit/).

Create and activate a virtual environment.

Install your project in editable mode in the active virtual environment:

```console
pip-df sync
```

If you don't have one yet, this will generate a file named `requirements.txt`,
containing the exact version of all your application dependencies, as they were
installed.

When you add or remove dependencies of your project (via `setup.py` or favorite
build backend configuration), run `pip-df sync` again to update your
environment and `requirements.txt`.

To update one or more dependencies to the latest allowed version, run:

```console
pip-df sync --update DEPENDENCY1 --update DEPENDENCY2 ...
```

## How to

(TODO)

- Initial install (create a venv, and run `pip-df sync` which will install
  and generate `requirements.txt`)
- Add pip options (`--find-links`, `--extra-index-url`, etc: in `requirements.txt.in`)
- Add a dependency that is published in an index or accessible via
  `--find-links` (add it in `setup.py`)
- Install dependencies from direct URLs such as git (add it in `setup.py` and
  add the git reference in `requirements.txt.in`)
- Remove a dependency (remove it from `setup.py`)
- Update a dependency to the most recent version (`pip-df sync --update
  DEPENDENCY1 --update DEPENDENCY2`)
- Update all dependencies to the latest version (`pip-df sync --update-all` or
  remove `requirements.txt` and run `pip-df sync`)
- Deploy my project (`pip wheel --no-deps requirements.txt -e .
  --wheel-dir=release`, ship the release directory then run `pip install
  --no-index release/*.whl`).

## CLI reference

Global options:

```text
Usage: pip-df [OPTIONS] COMMAND [ARGS]...

  A simple pip freeze workflow for Python application developers.

Options:
  --python PYTHON       [default: python]
  -v, --verbose         [default: False]
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  sync
```

`sync` command options:

```text
Usage: pip-df sync [OPTIONS]

Options:
  -u, --update DEPENDENCY     Make sure DEPENDENCY is upgraded (or downgraded)
                              to the latest allowed version. If DEPENDENCY is
                              not part of your application dependencies
                              anymore, this option has no effect. This option
                              can be repeated.

  --update-all                Upgrade (or downgrade) all dependencies of your
                              application to the latest allowed version.

  --editable / --no-editable  Install the project in editable mode.  [default:
                              True]

  --help                      Show this message and exit.
```

## Roadmap

- Optionally uninstall unneeded dependencies.
- Support extras (e.g. for a `test` extra, we would have
  `requirements-test.txt` which includes `requirements.txt` and
  optionally `requirements-test.txt.in`).
- Support different target environements for the same project (e.g. different
  python versions, which may result in different packages being installed). Is this actually useful in practice ?
