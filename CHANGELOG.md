# pip-deepfreeze changelog

This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for
the upcoming release can be found in
<https://github.com/sbidoul/pip-deepfreeze/tree/master/news/>.

<!-- towncrier release notes start -->

## 2.3 (2024-07-02)


### Features

- Add support for pre-sync commands. ([#152](https://github.com/sbidoul/pip-deepfreeze/issues/152))


## 2.2 (2024-03-10)


### Features

- Pass `--no-input` to pip commands, to avoid silently blocking on user input. ([#131](https://github.com/sbidoul/pip-deepfreeze/issues/131))
- Use `uv`'s `--python` option to select the interpreter, instead of passing it as a
  `VIRTUAL_ENV` environment variable. This is more explicit and hopefully more resilient
  to changes in `uv`'s Python detection logic. ([#145](https://github.com/sbidoul/pip-deepfreeze/issues/145))


## 2.1 (2024-03-01)

### Deprecations and Removals

- Change `--installer=uv` to `--installer=uvpip`. This is a breaking
  change that we do while this is young, to avoid possible confusion in
  the future with other `uv` install mechanisms that are on their
  roadmap.
  ([\#144](https://github.com/sbidoul/pip-deepfreeze/issues/144))

## 2.0 (2024-02-25)

### Features

- Allow to declare minimum pip-deepfreeze version in `pyproject.toml`.
  `pip-deepfreeze` verifies its version according to
  `tool.pip-deepfreeze.min_version`, so a project can ensure all
  contributors have the minmum required version.
  ([\#95](https://github.com/sbidoul/pip-deepfreeze/issues/95))
- Always install `uv` as a dependency. Consequently, the `uv` extra is
  removed.
  ([\#143](https://github.com/sbidoul/pip-deepfreeze/issues/143))

## 1.8 (2024-02-23)

### Features

- Read constraints from `constraints.txt` (and fallback to
  `requirements.txt.in` if it is absent), as this name better matches
  the purpose of the file.
  ([\#59](https://github.com/sbidoul/pip-deepfreeze/issues/59))

### Bugfixes

- Improve compatibility with `uv`, by passing installer options via
  command line instead of requirements file (this does not change how
  options are set by the user in `constraints.txt` or
  `requirements.txt.in`).
  ([\#138](https://github.com/sbidoul/pip-deepfreeze/issues/138))

## 1.7 (2024-02-22)

### Features

- Support environments where pip is not installed.
  ([\#98](https://github.com/sbidoul/pip-deepfreeze/issues/98))
- Add experimental support for [uv](https://github.com/astral-sh/uv) as
  the installation command. A new `--installer` option is available to
  select the installer to use.
  ([\#135](https://github.com/sbidoul/pip-deepfreeze/issues/135))

## 1.6 (2024-01-10)

### Bugfixes

- Silence a deprecation warning about `pkg_resources`.
  ([\#133](https://github.com/sbidoul/pip-deepfreeze/issues/133))
- Sort requirement files by canonical requirement name to help ensure
  stability and comparability.
  ([\#134](https://github.com/sbidoul/pip-deepfreeze/issues/134))

## 1.5 (2024-01-05)

### Features

- Normalize distribution names in the generated lock files. This change,
  which will cause some churn in generated `requirements*.txt` files,
  was made following a setuptools 69 evolution that started preserving
  underscores in distribution names.
  ([\#132](https://github.com/sbidoul/pip-deepfreeze/issues/132))

## 1.4 (2023-10-08)

### Features

- Pin pip, setuptools, wheel and distribute when they are dependencies
  of the project. Before they were not pinned in the `requirements*.txt`
  lock file because they were not reported by pip freeze. Now we pin
  them but never propose to uninstall them.
  ([\#123](https://github.com/sbidoul/pip-deepfreeze/issues/123))

### Bugfixes

- Set working directory to project root when running post sync commands.
  ([\#126](https://github.com/sbidoul/pip-deepfreeze/issues/126))
- Don't attempt to fixup VCS direct URLs for older python versions. It
  did not work with python 2.7 and pip's legacy resolver that is the
  default with these older pythons does not need this workaround.
  ([\#127](https://github.com/sbidoul/pip-deepfreeze/issues/127))

## 1.3 (2023-09-14)

### Features

- Use `pip inspect` when the target pip supports it. This allows working
  in virtual environments where `setuptools` (and thus `pkg_resources`)
  are not installed.
  ([\#97](https://github.com/sbidoul/pip-deepfreeze/issues/97))
- Don't warn about the absence of the `wheel` package when using `pip`
  \>= 23.1.
  ([\#101](https://github.com/sbidoul/pip-deepfreeze/issues/101))
- Search for `py`, then `python` executable in `PATH` when the
  `--python` option is not provided. This should provide a better
  experience on
  [Windows](https://docs.python.org/3/using/windows.html#launcher) and
  for users of the the [Python Launcher for
  Unix](https://python-launcher.app/).
  ([\#100](https://github.com/sbidoul/pip-deepfreeze/issues/100))
- Support named editable requirements in constraint files
  (`requirements.txt.in`) and lock files (`requirements*.txt`).
  ([\#110](https://github.com/sbidoul/pip-deepfreeze/issues/110))
- Improved handling of the temporary requirements file created during
  sync. ([\#115](https://github.com/sbidoul/pip-deepfreeze/issues/115))
- Work around a pip limitation that causes repeated metadata
  recomputation for VCS URLs. When a constraint is provided with a VCS
  URL with a mutable reference, pip installs it but does not cache the
  wheel. During subsequent `pip-df sync` runs, the metadata is therefore
  recomputed (because it is not cached), but the wheel is never built
  because pip rightly considers it is already installed. So it is never
  cached and this causes performance issues. As a workaround we fixup
  `direct_url.json` with a fake commit to force reinstallation (and
  therefore caching of the wheel) during subsequent sync with the pinned
  commit id.
  ([\#119](https://github.com/sbidoul/pip-deepfreeze/issues/119))
- Add `pip-deepfreeze --version`.
  ([\#120](https://github.com/sbidoul/pip-deepfreeze/issues/120))

### Deprecations and Removals

- Drop support for running pip-deepfreeze under python 3.7. We still
  support 3.7 target environments.
  ([\#112](https://github.com/sbidoul/pip-deepfreeze/issues/112))

### Misc

- Use ruff for linting.
  ([\#106](https://github.com/sbidoul/pip-deepfreeze/issues/106))
- Use `tomli` with python \< 3.11, and the stdlib tomllib otherwise.
  ([\#62](https://github.com/sbidoul/pip-deepfreeze/issues/62))

## 1.2 (2023-04-10)

### Features

- Don't show a stack trace when a post sync commands fails.
  ([\#91](https://github.com/sbidoul/pip-deepfreeze/issues/91))

### Bugfixes

- Avoid needlessly reinstalling Direct URL requirements that are not
  pinned exactly as pip freeze does.
  ([\#93](https://github.com/sbidoul/pip-deepfreeze/issues/93))

## 1.1 (2023-02-12)

### Features

- Read some configuration defaults from `pyproject.toml`.
  ([\#83](https://github.com/sbidoul/pip-deepfreeze/issues/83))
- Support pyproject.toml without build system to detect project name.
  ([\#84](https://github.com/sbidoul/pip-deepfreeze/issues/84))
- Add post-sync commands.
  ([\#86](https://github.com/sbidoul/pip-deepfreeze/issues/86))

### Bugfixes

- Read pyproject.toml using utf-8 encoding.
  ([\#90](https://github.com/sbidoul/pip-deepfreeze/issues/90))

### Deprecations and Removals

- Drop support for running pip-deepfreeze under python 3.6. We still
  support 3.6 target environments.
  ([\#88](https://github.com/sbidoul/pip-deepfreeze/issues/88))

## 1.0 (2022-09-27)

Release 1.0, no feature change.

## 0.10.1 (2022-09-07)

### Deprecations and Removals

- Remove `--no-use-pip-constraints` option. Users should switch to a pip
  version that supports URL constraints, which is all of them for the
  legacy resolver, and 21.1+ for the new resolver.
  ([\#60](https://github.com/sbidoul/pip-deepfreeze/issues/60))
- An editable installation of the project is now always done by
  pip-deepfreeze. The <span class="title-ref">--editable</span> option
  is removed as well as the attempt to detect if the project is
  editable. This allows correct support for projects that support PEP
  660 and do not have a <span class="title-ref">setup.py</span>.
  ([\#65](https://github.com/sbidoul/pip-deepfreeze/issues/65))

## v0.9.0 (2020-12-27)

### Features

- Now that PEP 621 is in provisional state, use it to detect the project
  name. ([\#56](https://github.com/sbidoul/pip-deepfreeze/issues/56))
- Rename `--extra` short option from `-e` to `-x`, to avoid confusion
  with pip's `-e` which is for editables.
  ([\#57](https://github.com/sbidoul/pip-deepfreeze/issues/57))

### Bugfixes

- Fixed an issue that prevented running `pip-df sync` after adding an
  extra to the setup.py/setup.cfg of an already installed project.
  ([\#49](https://github.com/sbidoul/pip-deepfreeze/issues/49))
- `pip-df sync --extras` now warns but otherwise ignores unknown extras.
  ([\#50](https://github.com/sbidoul/pip-deepfreeze/issues/50))

### Misc

- Fix issue with py39 tests on windows.
  ([\#53](https://github.com/sbidoul/pip-deepfreeze/issues/53))
- Update tests for pip new resolver compatibility.
  ([\#58](https://github.com/sbidoul/pip-deepfreeze/pull/58))

## v0.8.0 (2020-08-22)

Minor documentation improvements and internal tweaks.

## v0.7.0 (2020-08-14)

### Features

- Support extras.
  ([\#9](https://github.com/sbidoul/pip-deepfreeze/issues/9))
- Check prerequisites (pip, setuptools/pkg_resources) in the target
  environment.
  ([\#37](https://github.com/sbidoul/pip-deepfreeze/issues/37))
- Refuse to start if the target python is not running in a virtualenv,
  or if the virtualenv includes system site packages. This would be
  dangerous, risking removing or updating system packages.
  ([\#38](https://github.com/sbidoul/pip-deepfreeze/issues/38))
- Python 3.9 compatibility.
  ([\#45](https://github.com/sbidoul/pip-deepfreeze/issues/45))
- Improved logging of changes made to `requirements*.txt`.
  ([\#46](https://github.com/sbidoul/pip-deepfreeze/issues/46))

### Bugfixes

- Improve project name detection robustness.
  ([\#39](https://github.com/sbidoul/pip-deepfreeze/issues/39))

### Documentation

- Improved the documentation with the *How to* section.

## v0.6.0 (2020-08-03)

### Features

- Use `pip`'s `--constraints` mode by default when passing pinned
  dependencies and constraints to pip. In case this causes trouble (e.g.
  when using direct URLs with the new pip resolver), this can be
  disabled with `--no-use-pip-constraints`.
  ([\#31](https://github.com/sbidoul/pip-deepfreeze/issues/31))
- `--update` is changed to accept a comma-separated list of distribution
  names. ([\#33](https://github.com/sbidoul/pip-deepfreeze/issues/33))
- Add `--extras` option to `pip-df tree` command, to consider `extras`
  of the project when printing the tree of installed dependencies.
  ([\#34](https://github.com/sbidoul/pip-deepfreeze/issues/34))

## v0.5.0 (2020-07-27)

### Features

- Add -p short option for selecting the python interpreter (same as
  --python).
  ([\#27](https://github.com/sbidoul/pip-deepfreeze/issues/27))
- Add --project-root global option, to select the project directory.
  ([\#28](https://github.com/sbidoul/pip-deepfreeze/issues/28))
- Add `tree` command to print the installed dependencies of the project
  as a tree. The print out includes the installed version (and direct
  URL if any), and highlights missing dependencies.
  ([\#29](https://github.com/sbidoul/pip-deepfreeze/issues/29))
- Add built-in knowledge of some build backends (setuptools' setup.cfg,
  flit, generic PEP 621) so we can obtain the project name faster,
  without doing a full PEP 517 metadata preparation.
  ([\#30](https://github.com/sbidoul/pip-deepfreeze/issues/30))

### Misc

- Refactor installed dependencies discovery.
  ([\#26](https://github.com/sbidoul/pip-deepfreeze/issues/26))

## v0.4.0 (2020-07-21)

### Features

- Add `--uninstall-unneeded` option to uninstall distributions that are
  not dependencies of the project.
  ([\#11](https://github.com/sbidoul/pip-deepfreeze/issues/11))
- More complete and visible logging. We log the main steps in blue to
  distinguish them from pip logs.
  ([\#16](https://github.com/sbidoul/pip-deepfreeze/issues/16))
- Windows and macOS compatibility.
  ([\#17](https://github.com/sbidoul/pip-deepfreeze/issues/17))
- Add `--verbose` option.
  ([\#22](https://github.com/sbidoul/pip-deepfreeze/issues/22))

## v0.3.0 (2020-07-19)

### Features

- Better reporting of subprocess errors.
  ([\#6](https://github.com/sbidoul/pip-deepfreeze/issues/6))
- For now we do not use `pip install --constraints` because it has
  limitations and does not support VCS references with the new pip
  resolver. ([\#7](https://github.com/sbidoul/pip-deepfreeze/issues/7))

### Bugfixes

- Fix pkg_resources.VersionConflict error when downgrading an already
  installed dependency.
  ([\#10](https://github.com/sbidoul/pip-deepfreeze/issues/10))

## v0.2.0 (2020-07-16)

### Features

- Better UX if the project does not support editable. Default to
  editable mode if the project supports it. Fail gracefully if editable
  mode is requested for a project that does not support it.
  ([\#2](https://github.com/sbidoul/pip-deepfreeze/issues/2))
- Detect requirement name of the form egg=name.
  ([\#3](https://github.com/sbidoul/pip-deepfreeze/issues/3))

## v0.1.0 (2020-07-15)

First release.
