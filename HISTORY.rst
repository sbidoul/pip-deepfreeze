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
