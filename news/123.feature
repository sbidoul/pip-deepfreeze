Pin pip, setuptools, wheel and distribute when they are dependencies of the project.
Before they were not pinned in the ``requirements*.txt`` lock file because they were not
reported by pip freeze. Now we pin them but never propose to uninstall them.
