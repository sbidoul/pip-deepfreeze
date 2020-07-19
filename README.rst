pip-deepfreeze
==============

A simple pip freeze workflow for Python application developers.

.. image:: https://img.shields.io/github/workflow/status/sbidoul/pip-deepfreeze/CI
   :target: https://github.com/sbidoul/pip-deepfreeze/actions?query=workflow%3ACI
   :alt: GitHub Workflow Status

.. image:: https://img.shields.io/codecov/c/github/sbidoul/pip-deepfreeze
   :target: https://codecov.io/gh/sbidoul/pip-deepfreeze
   :alt: Codecov

.. image:: https://img.shields.io/pypi/v/pip-deepfreeze?label=pypi%20package
   :target: https://pypi.org/project/pip-deepfreeze/
   :alt: PyPI

.. contents::

About
-----

``pip-deepfreeze`` aims at doing one thing and doing it well, namely installing and
pinning dependencies of Python applications (not libraries) in a virtual environment.

- It is easy to use.
- It is fast.
- It relies on the documented ``pip`` command line interface and its
  ubiquitous `requirements file
  format <https://pip.pypa.io/en/stable/user_guide/?highlight=requirements#requirements-files>`__.
- It assumes your project is configured using a PEP 517 compliant build
  backend but otherwise makes no assumption on the specific backend
  used.
- It has first class support for VCS references.
- It is written in Python 3.6+, yet works in any virtual environment
  that has ``pip`` installed, including python 2.
- It is small, simple, with good test coverage and hopefully easy to
  maintain.

.. warning::

   While ``pip-deepfreeze`` is functional already (see `roadmap below <#roadmap>`__), this
   is to be considered as alpha software for a little while, until we have gathered some
   feedback on the CLI options.

Installation
------------

Using `pipx <https://pypi.org/project/pipx/>`__ (recommended):

.. code:: console

    pipx install pip-deepfreeze

Using `pip <https://pypi.org/project/pip/>`__:

.. code:: console

    pip install --user pip-deepfreeze

.. note::

   It is *not* recommended to install ``pip-deepfreeze`` in the same environment as your
   application, so its dependencies do not interfere with your app. By default it works
   with the ``python`` found in your ``PATH`` (which does what you normally expect in an
   activated virtualenv), but you can ask it to work within another environment using
   the ``--python`` option.

Quick start
-----------

Make sure your application declares its dependencies using `setuptools
<https://pypi.org/project/setuptools/>`__ (via the ``install_requires`` key in
``setup.py`` or ``setup.cfg``), or any other compliant `PEP 517
<https://www.python.org/dev/peps/pep-0517/>`__ build backend such as `flit
<https://pypi.org/project/flit/>`__.

First of all, create and activate a virtual environment using your favorite
tool. Run ``pip list`` to make sure ``pip``, ``setuptools`` and ``wheel`` are
installed in the virtualenv.

To install your project (in editable mode if supported) in the active virtual
environment, go to your project root directory and run:

.. code:: console

    pip-df sync

If you don't have one yet, this will generate a file named ``requirements.txt``,
containing the exact version of all your application dependencies, as they were
installed.

You can then add this ``requirement.txt`` to version control, and other people
collaborating on the project can install the project and its known good
dependencies using ``pip-df sync`` (or ``pip install -r requirements.txt -e .``
in a fresh virtualenv).

When you add or remove dependencies of your project, run ``pip-df sync`` again
to update your environment and ``requirements.txt``.

To update one or more dependencies to the latest allowed version, run:

.. code:: console

    pip-df sync --update DEPENDENCY1 --update DEPENDENCY2 ...

If you need to add some dependencies from VCS references (e.g. when a library
with a patch you need is not available as a release on a package index), add
the dependency as usual in your project, then add the VCS reference to a file
named ``requirements.txt.in`` like this::

   DEPENDENCYNAME @ git+https://g.c/org/project@branch

Then run ``pip-df sync``. It will update ``requirements.txt`` with a VCS
reference pinned at the exact commit that was installed (you need pip version
20.1 or greater for this to work). If later you need to update to the HEAD of
the same branch, simply use ``pip-df sync --update DEPENDENCYNAME``.

When, later again, your branch is merged upstream and the project has published
a release, remove the line from ``requirements.txt.in`` and run ``pip-df sync
--update DEPENDENCYNAME`` to update to the latest released version.

How to
------

(TODO)

-  Initial install (create a venv, and run ``pip-df sync`` which will
   install and generate ``requirements.txt``)
-  Add pip options (``--find-links``, ``--extra-index-url``, etc: in
   ``requirements.txt.in``)
-  Add a dependency that is published in an index or accessible via
   ``--find-links`` (add it in ``setup.py``)
-  Install dependencies from direct URLs such as git (add it in
   ``setup.py`` and add the git reference in ``requirements.txt.in``)
-  Remove a dependency (remove it from ``setup.py``)
-  Update a dependency to the most recent version
   (``pip-df sync --update   DEPENDENCY1 --update DEPENDENCY2``)
-  Update all dependencies to the latest version
   (``pip-df sync --update-all`` or remove ``requirements.txt`` and run
   ``pip-df sync``)
-  Pass options to pip (via ``requirements.txt.in`` or via ``PIP_*``
   environment variables)
-  Deploy my project
   (``pip wheel --no-deps requirements.txt -e . --wheel-dir=release``, ship the
   release directory then run ``pip install   --no-index release/*.whl``).

CLI reference
-------------

Global options::

    Usage: pip-df [OPTIONS] COMMAND [ARGS]...

      A simple pip freeze workflow for Python application developers.

    Options:
      --python PYTHON       [default: python]
      --install-completion  Install completion for the current shell.
      --show-completion     Show completion for the current shell, to copy it or
                            customize the installation.

      --help                Show this message and exit.

    Commands:
      sync

``sync`` command options::

    Usage: pip-df sync [OPTIONS]

    Options:
      -u, --update DEPENDENCY     Make sure DEPENDENCY is upgraded (or downgraded)
                                  to the latest allowed version. If DEPENDENCY is
                                  not part of your application dependencies
                                  anymore, this option has no effect. This option
                                  can be repeated.

      --update-all                Upgrade (or downgrade) all dependencies of your
                                  application to the latest allowed version.

      --editable / --no-editable  Install the project in editable mode. Defaults
                                  to editable if the project supports it.

      --help                      Show this message and exit.

Roadmap
-------

-  Stabilize CLI options.
-  Optionally uninstall unneeded dependencies.
-  Support extras (e.g. for a ``test`` extra, we would have
   ``requirements-test.txt`` which includes ``requirements.txt`` and
   optionally ``requirements-test.txt.in``).
-  Support different target environements for the same project (e.g.
   different python versions, which may result in different packages
   being installed). Is this actually useful in practice ?

Development
-----------

To run tests, use ``tox``. You will get a test coverage report in
``htmlcov/index.html``. An easy way to install tox is ``pipx install tox``.

This project uses `pre-commit <https://pre-commit.com/>`__ to enforce linting
(among which `black <https://pypi.org/project/black/>`__ for code formating,
`isort <https://pypi.org/project/isort/>`__ for sorting imports, and `mypy
<https://pypi.org/project/mypy/>`__ for type checking).

To make sure linters run locally on each of your commits, install pre-commit
(``pipx install pre-commit`` is recommended), and run ``pre-commit install`` in
your local clone of the ``pip-deepfreeze`` repository.

To release:

- Select the next version number of the form ``x.y.z``.
- ``towncrier --version x.y.z``.
- Inspect and commit the updated ``HISTORY.rst``.
- ``git tag x.y.z ; git push --tags``.
