# pip-deepfreeze

![image](https://raw.githubusercontent.com/sbidoul/pip-deepfreeze/master/docs/logo.png)

A simple pip freeze workflow for Python application developers.

[![PyPI](https://img.shields.io/pypi/v/pip-deepfreeze?label=pypi%20package)](https://pypi.org/project/pip-deepfreeze/)
[![PyPI - License](https://img.shields.io/pypi/l/pip-deepfreeze)](https://github.com/sbidoul/pip-deepfreeze/blob/master/LICENSE.txt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pip-deepfreeze)](https://pypi.org/project/pip-deepfreeze/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/sbidoul/pip-deepfreeze/ci.yml?label=CI)](https://github.com/sbidoul/pip-deepfreeze/actions)

Table of contents

- [About](#about)
- [Intallation](#installation)
- [Quick Start](#quick-start)
- [How to](#how-to)
- [FAQ](#faq)
- [CLI Reference](#cli-reference)
- [Other tools](#other-tools)
- [Development](#development)
- [Contributing](#contributing)

## About

`pip-deepfreeze` aims at doing one thing and doing it well, namely
managing the dependencies of a Python *application* in a virtual
environment.

This includes:

- installing the project in editable mode, and its dependencies,
- updating the environment with new dependencies as the project evolves,
- uninstalling unused dependencies,
- refreshing dependencies,
- maintaining pinned dependencies in `requirements.txt` lock files,
- maintaining pinned optional dependencies in `requirements-{extra}.txt` lock files,
- displaying installed dependencies as a tree.

A few characteristics of this project:

- It is easy to use, with a single `pip-df sync` command.
- It is fast, with very little overhead on top of a regular
  `pip install` + `pip freeze`.
- It relies on the documented `pip` command line interface and its
  ubiquitous [requirements file
  format](https://pip.pypa.io/en/stable/user_guide/?highlight=requirements#requirements-files).
- It assumes your project is configured using a PEP 517/660 compliant
  build backend but otherwise makes no assumption on the specific
  backend used.
- It has first class support for dependencies specified as VCS
  references.
- It is written in Python 3.8+, yet works in any virtual environment
  that has `pip` installed, including python 2 and python 3.6 and 3.7.
- It works with pip-less virtual environments created with
  `python3 -m venv --without-pip`.
- It is reasonably small and simple, with good test coverage and is
  hopefully easy to maintain.

## Installation

Using [pipx](https://pypi.org/project/pipx/) (recommended):

``` console
pipx install pip-deepfreeze
```

Using [pip](https://pypi.org/project/pip/):

``` console
pip install --user pip-deepfreeze
```

> [!IMPORTANT]
> It is *not* recommended to install `pip-deepfreeze` in the same
> environment as your application, so its dependencies do not interfere
> with your app. By default it works with the `py` or `python`
> executable found in your `PATH` (which does what you normally expect
> in an activated virtualenv), but you can ask it to work within another
> environment using the `--python` option.

## Quick start

![pip-deepfreeze synopsis](https://raw.githubusercontent.com/sbidoul/pip-deepfreeze/41e960aecd1b142bad648d438143f55b6f50bba5/docs/synopsis.png)

Make sure your application declares its direct dependencies in
[pyproject.toml](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/),
or any other mechanism supported by your PEP 517/660 compliant build
backend.

Create and activate a virtual environment using your favorite tool.

> [!TIP]
> When you install `pip-deepfreeze`, it also installs `pip` so you don't
> need to install `pip` separately in your virtual environment (for
> instance, you may use `python3 -m venv --without-pip` to create it).
> However, if your virtual environment uses a Python version that is not
> supported by `pip-deepfreeze`'s bundled copy of `pip`, you will need
> to install `pip` in the target virtual environment.

> [!IMPORTANT]
> When using `pip` older than 23.1, you may need to also install
> `setuptools` and `wheel` in the virtual environment for best results.

To install your project in editable mode in the active virtual
environment, go to your project root directory and run:

``` console
pip-df sync
```

If you don't have one yet, this will generate a file named
`requirements.txt`, containing the exact version of all your application
dependencies, as they were installed.

You can then add this `requirement.txt` to version control, and other
people collaborating on the project can install the project and its
known good dependencies using `pip-df sync` (or
`pip install -r requirements.txt -e .` in a fresh virtualenv).

> [!TIP]
> `pip-deepfreeze` has experimental support for the [uv
> pip](https://github.com/astral-sh/uv) installer. To use it, run
> `pip-df sync --installer=uvpip`.

When you add or remove dependencies of your project, run `pip-df sync`
again to update your environment and `requirements.txt`.

To update one or more dependencies to the latest allowed version, run:

``` console
pip-df sync --update DEPENDENCY1,DEPENDENCY2 ...
```

If you need to add some dependencies from VCS references (e.g. when a
library with a patch you need is not available as a release on a package
index), add the dependency as usual in your project, then add the VCS
reference to a file named `constraints.txt` like this:

    DEPENDENCYNAME @ git+https://g.c/org/project@branch

Then run `pip-df sync`. It will update `requirements.txt` with a VCS
reference pinned at the exact commit that was installed (you need pip
version 20.1 or greater for this to work). If later you need to update
to the HEAD of the same branch, simply use
`pip-df sync --update DEPENDENCYNAME`.

When, later again, your branch is merged upstream and the project has
published a release, remove the line from `constraints.txt` and run
`pip-df sync --update DEPENDENCYNAME` to update to the latest released
version.

## How to

Creating a new project.

> Follow the instructions of your favorite PEP 517/660 compliant build
> tool, such as `hatch`, `setuptools`, `flit` or others. After declaring
> the first dependencies, create and activate a virtualenv, then run
> `pip-df sync` in the project directory to generate pinned dependencies
> in `requirements.txt`.

Installing an existing project.

> After checking out the project from source control, create and
> activate activate virtualenv, the run `pip-df sync` to install the
> project.

Updating to the latest version of a project.

> After dependencies have been added to the project by others, update
> the source code from VCS, then run `pip-df sync` while in your
> activated virtualenv to bring it to the desired state: dependencies
> will be updated, removed or uninstalled as needed.

Adding or removing dependencies.

> After you have added or removed dependencies to your build tool
> configuration, simply run `pip-df sync` to update your virtualenv. You
> will be prompted to uninstall unneeded dependencies.

Refreshing some pinned dependencies.

> After a while you may want to refresh some or all of your dependencies
> to an up-to-date version. You can do so with
> `pip-df sync --update dep1,dep2,...`.

Refreshing all pinned dependencies.

> To update all dependencies to the latest allowed version, you can use
> `pip-df sync --update-all`. This is equivalent to removing
> `requirements.txt` then running `pip-df sync`. This is also roughly
> equivalent to reinstalling in an empty virtualenv with
> `pip install -e . -c constraints.txt` then running
> `pip freeze > requirements.txt`.

Using another package index than PyPI.

> Create a file named `constraints.txt` in your project root, and add
> pip options to it, such as `--index-url` or `--find-links`. You
> can add any option that [pip supports in requirements
> files](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).

Installing dependencies from VCS.

> When one of your direct or indirect dependencies has a bug or a
> missing feature, it is convenient to do an upstream pull request then
> install from it. Assume for instance your project depends on the
> `packaging` library and you want to install a pull request you made to
> it. To do so, make sure `packaging` is declared as a regular
> dependency of your project. Then add the VCS reference in
> `constraints.txt` like so:
>
>     packaging @ git+https://github.com/you/packaging@your-branch
>
> Then run `pip-df sync --update packaging` to install from the branch
> and pin the exact commit in `requirements.txt` for reproducibility.
> When upstream merges your PR and cuts a release, you can simply remove
> the line from `constraints.txt` and run
> `pip-df sync --update packaging` to refresh to the latest released
> version.

Working with extras.

> Assuming your project configuration declares extra dependencies such
> as `tests` or `docs`, you can run `pip-df sync --extras tests,docs` to
> update your virtualenv with the necessary dependencies. This will also
> pin extra dependencies in `requirements-tests.txt` and
> `requirements-docs.txt`. Note that pip-deepfreeze assumes that the
> `extras` mechanism is used to specify *additional* dependencies to the
> base dependencies of the project.

## FAQ

What should I put in `constraints.txt`? Should I add all my dependencies
there?

> `constraints.txt` is optional. The dependencies of your project must
> be declared primarily in `pyproject.toml` (or the legacy
> `setup.py/setup.cfg`). `constraints.txt` may contain additional
> constraints if needed, such as version constraints on indirect
> dependencies that you don't control, or VCS links for dependencies
> that you need to install from VCS source.

I have added a constraint in `constraints.txt` but `pip-df sync` does
not honor it. What is going on?

> `pip-df sync` always gives priority to versions pinned in
> `requirements.txt`, unless explicitly asked to do otherwise. After
> adding or changing constraints or VCS references for already pinned
> requirements, use the `--update` option like so:
>
>     pip-df sync --update DEPENDENCY1,DEPENDENCY2,...

`pip-deepfreez` erroneously complains
python is not running in a virtualenv.

> The most probable cause is that you used an older version of
> `virtualenv` which does not generate PEP 405 compliant virtual
> environments. `virtualenv` version 20 and later are supported, as well
> as the Python 3 native `venv` module. Should this problem be prevalent
> in practice, we may add support for older `virtualenv` versions, or
> add an option to ignore the virtualenv sanity check (which is only
> there to prevent `pip-deepfreeze` to corrupt the system Python
> packages by accident).

How can I pass options to pip?

> The most reliable and repeatable way to pass options to pip is to add
> them in `constraints.txt`. The pip documentation lists [options that
> are allowed in requirements
> files](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).
> Global options can also be set in the pip configuration file or passed
> via `PIP_*` environment variables (see the pip documentation for more
> information).

Why not using `pip install` and `pip freeze` manually?

> `pip-df sync` combines both commands in one and ensures your
> environment and pinned requirements remain correct and up-to-date.
> Some error prone operations it facilitates include: uninstalling
> unneeded dependencies, updating selected dependencies, overriding
> dependencies with VCS references, etc.

Is there a recommended way to deploy my project in the production
environment?

> There are many possibilities. One approach that works well (and is
> recommended in the pip documentation) works with two simple steps.
> First you build the wheel files for your project and dependencies,
> using:
>
>     pip wheel --no-deps -r requirements.txt -e . --wheel-dir=./wheel-dir
>
> Then you ship the content of the `wheel-dir` directory to your target
> environment or docker image, and run:
>
>     pip install --no-index --find-links=./wheel-dir project-name
>
> Note the use of `--no-deps` when building and `--no-index` when
> installing. This will ensure that all the required dependencies are
> effectively pinned in `requirements.txt`.

## CLI reference

> [!NOTE]
> The command line interface is the only supported public interface. If
> you find yourself writing `import pip_deepfreeze`, please don't, as
> everything may change without notice. Or rather, get in touch to
> discuss your needs.

### Global options

```
Usage: pip-df [OPTIONS] COMMAND [ARGS]...

A simple pip freeze workflow for Python application developers.

Options:
  -p, --python, --py PYTHON     The python executable to use. Determines the
                                python environment to work on. Defaults to the
                                'py' or 'python' executable found in PATH.
  -r, --project-root DIRECTORY  The project root directory.  [default: .]
  --min-version      VERSION    Minimum version of pip-deepfreeze required.
  --version                     Show the version and exit.
  -v, --verbose
  --install-completion          Install completion for the current shell.
  --show-completion             Show completion for the current shell, to copy
                                it or customize the installation.
  --help                        Show this message and exit.

Commands:
  sync  Install/update the environment to match the project requirements.
  tree  Print the installed dependencies of the project as a tree.
```

### pip-df sync

```
Usage: pip-df sync [OPTIONS]

  Install/update the environment to match the project requirements, and lock new
  dependencies.

  Install/reinstall the project. Install/update dependencies to the latest
  allowed version according to pinned dependencies in requirements.txt or
  constraints in constraints.txt. On demand update of dependencies to to
  the latest version that matches constraints. Optionally uninstall unneeded
  dependencies.

Options:
  -u, --update DEP1,DEP2,...      Make sure selected dependencies are upgraded
                                  (or downgraded) to the latest allowed
                                  version. If DEP is not part of your
                                  application dependencies anymore, this
                                  option has no effect.

  --update-all                    Upgrade (or downgrade) all dependencies of
                                  your application to the latest allowed
                                  version.

  -x, --extras EXTRA1,EXTRA2,... Comma separated list of extras to install
                                  and freeze to requirements-{EXTRA}.txt.

  --post-sync-command TEXT        Command to run after the sync operation is
                                  complete. Can be specified multiple times.

  --uninstall-unneeded / --no-uninstall-unneeded
                                  Uninstall distributions that are not
                                  dependencies of the project. If not
                                  specified, ask confirmation.

  --installer [pip|uvpip]

  --help                          Show this message and exit.
```

### pip-df tree

```
Usage: pip-df tree [OPTIONS]

  Print the installed dependencies of the project as a tree.

Options:
  -x, --extras EXTRA1,EXTRA2,...  Extras of project to consider when looking for
                                  dependencies.

  --help                          Show this message and exit.
```

## Configuration

Most options can get default values from a `[tool.pip-deepfreeze]`
section of your `pyproject.toml` file. For instance:

- `sync.extras`: default value for the `--extras` option of the `sync`
  command.
- `sync.post_sync_commands`: default value (as a list of strings) for
  the `--post-sync-command` options of the `sync` command.
- `sync.installer`
- `min_version`

Example:

``` toml
[tool.pip-deepfreeze]
min_version = "2.0"

[tool.pip-deepfreeze.sync]
extras = "test,doc"
post_sync_commands = ["pip-preserve-requirements requirements*.txt"]
installer = "uvpip"
```

## Other tools

Several other tools exist with a similar or overlapping scope as
`pip-deepfreeze`.

- [pip](https://pip.pypa.io/en/stable/) itself. `pip-deepfreeze` relies
  extensively on the `pip` CLI for installation and querying the
  database of installed distributions. In essence it is a thin wrapper
  around `pip install` and `pip freeze`. Some of the features here may
  serve as inspiration for future `pip` evolutions.
- [pip-tools](https://pypi.org/project/pip-tools/). This is the one with
  the most similar features. Besides the reasons explained in
  [About](#about) above I wanted to see if it was possible to do such a
  thing using the `pip` CLI only. `pip-deepfreeze` is also more
  opinionated than `pip-tools` and `pipdeptree`, as it always does an
  editable install and it uses the build backend to obtain the top level
  dependencies.
- [uv](https://pypi.org/project/uv/)
- [PDM](https://pypi.org/project/pdm/)
- [Poetry](https://python-poetry.org/)
- [pipenv](https://pipenv.pypa.io/en/latest/)
- [pipdeptree](https://pypi.org/project/pipdeptree/). Works similarly as
  `pip-df tree`. It is convenient to have a tree command in pip-deepfreeze, that
  shares the exact same notion of top level dependencies.

## Development

To run tests, use `tox`. You will get a test coverage report in
`htmlcov/index.html`. An easy way to install tox is `pipx install tox`.

This project uses [pre-commit](https://pre-commit.com/) to enforce
linting (among which [black](https://pypi.org/project/black/) for code
formating, [isort](https://pypi.org/project/isort/) for sorting imports,
and [mypy](https://pypi.org/project/mypy/) for type checking).

To make sure linters run locally on each of your commits, install
pre-commit (`pipx install pre-commit` is recommended), and run
`pre-commit install` in your local clone of the `pip-deepfreeze`
repository.

To release:

- Select the next version number of the form `X.Y(.Z)`.
- `towncrier --version X.Y(.Z)`.
- Inspect and commit the updated `CHANGELOG.md`.
- On GitHub, create a new release. Choose a tag of the form `vX.Y(.Z)`. Click `Generate
  release notes` and copy over the content from `CHANGELOG.md`.

## Contributing

We welcome contributions of all kinds.

Please consult the [issue
tracker](https://github.com/sbidoul/pip-deepfreeze/issues) to discover
the roadmap and known bugs.

Before opening a pull request, please create an issue first to discuss
the bug or feature request.
