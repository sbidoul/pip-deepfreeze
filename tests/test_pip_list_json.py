from __future__ import unicode_literals

import json
import os
import subprocess

import pytest

# /!\ this test file must be python 2 compatible /!\
PIP_LIST_JSON = os.path.join(
    os.path.dirname(__file__), "..", "src", "pip_deepfreeze", "pip_list_json.py"
)


@pytest.mark.parametrize(
    "to_install, expected",
    [
        (
            ["pkgb", "pkgc", "pkgd", "pkge"],
            [
                {"metadata": {"name": "pkga", "version": "0.0.0"}},
                {
                    "metadata": {
                        "name": "pkgb",
                        "version": "0.0.0",
                        "requires_dist": ["pkga<0.0.1"],
                    },
                    "requires": ["pkga"],
                },
                {"metadata": {"name": "pkgc", "version": "0.0.3"}},
                {
                    "metadata": {
                        "name": "pkgd",
                        "version": "0.0.0",
                        "requires_dist": [
                            "pkga",
                            'pkgb; extra == "b"',
                            'pkgc<0.0.3; extra == "c"',
                        ],
                        "provides_extra": ["b", "c"],
                    },
                    "requires": ["pkga"],
                    "extra_requires": {"c": ["pkgc"], "b": ["pkgb"]},
                },
                {
                    "metadata": {
                        "name": "pkge",
                        "version": "0.0.0",
                        "requires_dist": ["pkgd[b,c]"],
                    },
                    "requires": ["pkgd[b,c]"],
                },
            ],
        )
    ],
)
def test_pip_list_json(to_install, expected, virtualenv_python, testpkgs):

    subprocess.check_call(
        [
            virtualenv_python,
            "-m",
            "pip",
            "install",
            "--find-links",
            testpkgs,
            "pytest-cov",  # pytest-cov needed for subprocess coverage to work
        ]
        + to_install
    )
    depends_str = subprocess.check_output(
        [virtualenv_python, PIP_LIST_JSON], universal_newlines=True,
    )
    depends_list = json.loads(depends_str)
    depends = sorted(
        [
            rec
            for rec in depends_list
            if rec["metadata"]["name"] in ("pkga", "pkgb", "pkgc", "pkgd", "pkge")
        ],
        key=lambda r: r["metadata"]["name"],
    )
    assert depends == expected
