 0.3.0 (2020-07-19)
===================

Features
--------

- Better reporting off subprocess errors. (`#6 <https://github.com/sbidoul/pip-deepfreeze/issues/6>`_)
- For now we do not use ``pip install --constraints`` because it has limitations,
  and does not work with the new pip resolver. (`#7 <https://github.com/sbidoul/pip-deepfreeze/issues/7>`_)


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
