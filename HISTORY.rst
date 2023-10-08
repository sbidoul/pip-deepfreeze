v1.4.0 (2023-10-08)
===================

Features
--------

- Pin pip, setuptools, wheel and distribute when they are dependencies of the project.
  Before they were not pinned in the ``requirements*.txt`` lock file because they were not
  reported by pip freeze. Now we pin them but never propose to uninstall them. (`#123 <https://github.com/sbidoul/pip-deepfreeze/issues/123>`_)


Bugfixes
--------

- Set working directory to project root when running post sync commands. (`#126 <https://github.com/sbidoul/pip-deepfreeze/issues/126>`_)
- Don't attempt to fixup VCS direct URLs for older python versions. It did not work with
  python 2.7 and pip's legacy resolver that is the default with these older pythons does
  not need this workaround. (`#127 <https://github.com/sbidoul/pip-deepfreeze/issues/127>`_)


1.3 (2023-09-14)
================

Features
--------

- Use ``pip inspect`` when the target pip supports it. This allows working in virtual
  environments where ``setuptools`` (and thus ``pkg_resources``) are not installed. (`#97
  <https://github.com/sbidoul/pip-deepfreeze/issues/97>`_)
- Don't warn about the absence of the ``wheel`` package when using ``pip`` >= 23.1.
  (`#101 <https://github.com/sbidoul/pip-deepfreeze/issues/101>`_)
- Search for ``py``, then ``python``  executable in ``PATH`` when the ``--python``
  option is not provided. This should provide a better experience on `Windows
  <https://docs.python.org/3/using/windows.html#launcher>`_ and for users of the the
  `Python Launcher for Unix <https://python-launcher.app/>`_. (`#100
  <https://github.com/sbidoul/pip-deepfreeze/issues/100>`_)
- Support named editable requirements in constraint files (``requirements.txt.in``) and
  lock files (``requirements*.txt``). (`#110
  <https://github.com/sbidoul/pip-deepfreeze/issues/110>`_)
- Improved handling of the temporary requirements file created during sync. (`#115
  <https://github.com/sbidoul/pip-deepfreeze/issues/115>`_)
- Work around a pip limitation that causes repeated metadata recomputation for VCS URLs.
  When a constraint is provided with a VCS URL with a mutable reference, pip installs it
  but does not cache the wheel. During subsequent ``pip-df sync`` runs, the metadata is
  therefore recomputed (because it is not cached), but the wheel is never built because
  pip rightly considers it is already installed. So it is never cached and this causes
  performance issues. As a workaround we fixup ``direct_url.json`` with a fake commit to
  force reinstallation (and therefore caching of the wheel) during subsequent sync with
  the pinned commit id. (`#119 <https://github.com/sbidoul/pip-deepfreeze/issues/119>`_)
- Add ``pip-deepfreeze --version``. (`#120
  <https://github.com/sbidoul/pip-deepfreeze/issues/120>`_)


Deprecations and Removals
-------------------------

- Drop support for running pip-deepfreeze under python 3.7. We still support 3.7 target
  environments. (`#112 <https://github.com/sbidoul/pip-deepfreeze/issues/112>`_)


Misc
----

- Use ruff for linting. (`#106 <https://github.com/sbidoul/pip-deepfreeze/issues/106>`_)
- Use ``tomli`` with python < 3.11, and the stdlib tomllib otherwise. (`#62
  <https://github.com/sbidoul/pip-deepfreeze/issues/62>`_)


1.2.0 (2023-04-10)
==================

Features
--------

- Don't show a stack trace when a post sync commands fails. (`#91 <https://github.com/sbidoul/pip-deepfreeze/issues/91>`_)


Bugfixes
--------

- Avoid needlessly reinstalling Direct URL requirements that are not pinned exactly as pip
  freeze does. (`#93 <https://github.com/sbidoul/pip-deepfreeze/issues/93>`_)


1.1 (2023-02-12)
================

Features
--------

- Read some configuration defaults from ``pyproject.toml``. (`#83 <https://github.com/sbidoul/pip-deepfreeze/issues/83>`_)
- Support pyproject.toml without build system to detect project name. (`#84 <https://github.com/sbidoul/pip-deepfreeze/issues/84>`_)
- Add post-sync commands. (`#86 <https://github.com/sbidoul/pip-deepfreeze/issues/86>`_)


Bugfixes
--------

- Read pyproject.toml using utf-8 encoding. (`#90 <https://github.com/sbidoul/pip-deepfreeze/issues/90>`_)


Deprecations and Removals
-------------------------

- Drop support for running pip-deepfreeze under python 3.6. We still support 3.6 target
  environments. (`#88 <https://github.com/sbidoul/pip-deepfreeze/issues/88>`_)


1.0 (2022-09-27)
================

Release 1.0, no feature change.

0.10.1 (2022-09-07)
===================

Deprecations and Removals
-------------------------

- Remove ``--no-use-pip-constraints`` option. Users should switch to a pip
  version that supports URL constraints, which is all of them for the legacy
  resolver, and 21.1+ for the new resolver. (`#60 <https://github.com/sbidoul/pip-deepfreeze/issues/60>`_)
- An editable installation of the project is now always done by pip-deepfreeze. The
  `--editable` option is removed as well as the attempt to detect if the project is
  editable. This allows correct support for projects that support PEP 660 and do not have
  a `setup.py`. (`#65 <https://github.com/sbidoul/pip-deepfreeze/issues/65>`_)


v0.9.0 (2020-12-27)
===================

Features
--------

- Now that PEP 621 is in provisional state, use it to detect the project name. (`#56 <https://github.com/sbidoul/pip-deepfreeze/issues/56>`_)
- Rename ``--extra`` short option from ``-e`` to ``-x``, to avoid confusion with
  pip's ``-e`` which is for editables. (`#57 <https://github.com/sbidoul/pip-deepfreeze/issues/57>`_)


Bugfixes
--------

- Fixed an issue that prevented running ``pip-df sync`` after adding an extra to
  the setup.py/setup.cfg of an already installed project. (`#49 <https://github.com/sbidoul/pip-deepfreeze/issues/49>`_)
- ``pip-df sync --extras`` now warns but otherwise ignores unknown extras. (`#50 <https://github.com/sbidoul/pip-deepfreeze/issues/50>`_)


Misc
----

- Fix issue with py39 tests on windows. (`#53 <https://github.com/sbidoul/pip-deepfreeze/issues/53>`_)
- Update tests for pip new resolver compatibility. (`#58 <https://github.com/sbidoul/pip-deepfreeze/pull/58>`_)


v0.8.0 (2020-08-22)
===================

Minor documentation improvements and internal tweaks.

v0.7.0 (2020-08-14)
===================

Features
--------

- Support extras. (`#9 <https://github.com/sbidoul/pip-deepfreeze/issues/9>`_)
- Check prerequisites (pip, setuptools/pkg_resources) in the target environment. (`#37 <https://github.com/sbidoul/pip-deepfreeze/issues/37>`_)
- Refuse to start if the target python is not running in a virtualenv,
  or if the virtualenv includes system site packages. This would be dangerous,
  risking removing or updating system packages. (`#38 <https://github.com/sbidoul/pip-deepfreeze/issues/38>`_)
- Python 3.9 compatibility. (`#45 <https://github.com/sbidoul/pip-deepfreeze/issues/45>`_)
- Improved logging of changes made to ``requirements*.txt``. (`#46 <https://github.com/sbidoul/pip-deepfreeze/issues/46>`_)


Bugfixes
--------

- Improve project name detection robustness. (`#39 <https://github.com/sbidoul/pip-deepfreeze/issues/39>`_)

Documentation
-------------

- Improved the documentation with the *How to* section.


v0.6.0 (2020-08-03)
===================

Features
--------

- Use ``pip``'s ``--constraints`` mode by default when passing pinned
  dependencies and constraints to pip. In case this causes trouble (e.g. when
  using direct URLs with the new pip resolver), this can be disabled with
  ``--no-use-pip-constraints``. (`#31 <https://github.com/sbidoul/pip-deepfreeze/issues/31>`_)
- ``--update`` is changed to accept a comma-separated list of distribution names. (`#33 <https://github.com/sbidoul/pip-deepfreeze/issues/33>`_)
- Add ``--extras`` option to ``pip-df tree`` command, to consider ``extras`` of
  the project when printing the tree of installed dependencies. (`#34 <https://github.com/sbidoul/pip-deepfreeze/issues/34>`_)


v0.5.0 (2020-07-27)
===================

Features
--------

- Add -p short option for selecting the python interpreter (same as --python). (`#27 <https://github.com/sbidoul/pip-deepfreeze/issues/27>`_)
- Add --project-root global option, to select the project directory. (`#28 <https://github.com/sbidoul/pip-deepfreeze/issues/28>`_)
- Add ``tree`` command to print the installed dependencies of the project as a
  tree. The print out includes the installed version (and direct URL if any), and
  highlights missing dependencies. (`#29 <https://github.com/sbidoul/pip-deepfreeze/issues/29>`_)
- Add built-in knowledge of some build backends (setuptools' setup.cfg, flit,
  generic PEP 621) so we can obtain the project name faster, without doing
  a full PEP 517 metadata preparation. (`#30 <https://github.com/sbidoul/pip-deepfreeze/issues/30>`_)


Misc
----

- Refactor installed dependencies discovery. (`#26 <https://github.com/sbidoul/pip-deepfreeze/issues/26>`_)


v0.4.0 (2020-07-21)
===================

Features
--------

- Add ``--uninstall-unneeded`` option to uninstall distributions that are not
  dependencies of the project. (`#11 <https://github.com/sbidoul/pip-deepfreeze/issues/11>`_)
- More complete and visible logging. We log the main steps in blue to distinguish
  them from pip logs. (`#16 <https://github.com/sbidoul/pip-deepfreeze/issues/16>`_)
- Windows and macOS compatibility. (`#17 <https://github.com/sbidoul/pip-deepfreeze/issues/17>`_)
- Add ``--verbose`` option. (`#22 <https://github.com/sbidoul/pip-deepfreeze/issues/22>`_)


v0.3.0 (2020-07-19)
===================

Features
--------

- Better reporting of subprocess errors. (`#6 <https://github.com/sbidoul/pip-deepfreeze/issues/6>`_)
- For now we do not use ``pip install --constraints`` because it has limitations
  and does not support VCS references with the new pip resolver. (`#7
  <https://github.com/sbidoul/pip-deepfreeze/issues/7>`_)


Bugfixes
--------

- Fix pkg_resources.VersionConflict error when downgrading an already installed
  dependency. (`#10 <https://github.com/sbidoul/pip-deepfreeze/issues/10>`_)


v0.2.0 (2020-07-16)
===================

Features
--------

- Better UX if the project does not support editable. Default to editable
  mode if the project supports it. Fail gracefully if editable mode is requested
  for a project that does not support it. (`#2 <https://github.com/sbidoul/pip-deepfreeze/issues/2>`_)
- Detect requirement name of the form egg=name. (`#3 <https://github.com/sbidoul/pip-deepfreeze/issues/3>`_)

v0.1.0 (2020-07-15)
===================

First release.
