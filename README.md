# pip-deepfreeze

A simple pip freeze workflow for Python application developers.

## Installation

Using [pipx](https://pypi.org/project/pipx/) (recommended):

```console
pipx install pip-deepfreeze
```

Using [pip](https://pypi.org/project/pip/):

```console
pip install --user pip-deepfreeze
```

It is *not* recommended to install `pip-deepfreeze` in the same environment
as your application, so its dependencies do not interfere with your app.

## Quick start

Make sure your application declares its dependencies using setuptools (via the
`install_requires` key in `setup.py` or `setup.cfg`), or any other compliant
PEP 517 backend such as flit.

Create and activate a virtual environment.

Install your project in editable mode in the active virtual environment:

```console
pip-df sync
```

If you don't have one yet, this will generate a file named `requirements.txt`,
containing the exact version of all your application dependencies, as they were installed.

When you add dependencies to your project' `setup.py` (or your favorite build backend configuration), run `pip-df sync` again to update your environement and
`requirements.txt`.

To update a dependency, run:

```console
pip-df sync --update package
```

## How to

(TODO)
- initial install
- adding pip options (--find-links, --extra-index-url, etc)
- addint a dependency
- removing a dependency
- update a dependency to the most recent version
- update all dependencies to the latest version
- installing dependencies from direct URLs (such as git)

## Under the hood

(TODO) explain the principle of operations
- update frozen requirements.txt with constraints from requirements.txt.in
- pip freeze dependencies
- pip upgrade project
