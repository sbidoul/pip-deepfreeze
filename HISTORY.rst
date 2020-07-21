 0.4.0 (2020-07-21)
===================

Features
--------

- Add ``--uninstall-unneeded`` option to uninstall distributions that are not
  dependencies of the project. (`#11 <https://github.com/sbidoul/pip-deepfreeze/issues/11>`_)
- More complete and visible logging. We log the main steps in blue to distinguish
  them from pip logs. (`#16 <https://github.com/sbidoul/pip-deepfreeze/issues/16>`_)
- Windows and macOS compatibility. (`#17 <https://github.com/sbidoul/pip-deepfreeze/issues/17>`_)
- Add ``--verbose`` option. (`#22 <https://github.com/sbidoul/pip-deepfreeze/issues/22>`_)


0.3.0 (2020-07-19)
==================

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


0.2.0 (2020-07-16)
==================

Features
--------

- Better UX if the project does not support editable. Default to editable
  mode if the project supports it. Fail gracefully if editable mode is requested
  for a project that does not support it. (`#2 <https://github.com/sbidoul/pip-deepfreeze/issues/2>`_)
- Detect requirement name of the form egg=name. (`#3 <https://github.com/sbidoul/pip-deepfreeze/issues/3>`_)
