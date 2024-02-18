Add experimental support for `uv <https://github.com/astral-sh/uv>`_ as the installation
command. For now we still need `pip` to be installed in the target environment, to
inspect its content. A new ``--installer`` option is available to select the installer
to use.
