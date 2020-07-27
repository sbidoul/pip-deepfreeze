Add built-in knowledge of some build backends (setuptools' setup.cfg, flit,
generic PEP 621) so we can obtain the project name faster, without doing
a full PEP 517 metadata preparation.
