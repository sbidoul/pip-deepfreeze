import json
import os
from functools import lru_cache
from tempfile import TemporaryDirectory
from typing import cast

from packaging.markers import Environment
from packaging.tags import Tag, parse_tag

from .sanity import get_pip_command
from .utils import check_call, check_output

_SCRIPT = """\
import json
import sys

from packaging import markers, tags

json.dump(
    {
        "environment": markers.default_environment(),
        "tags": [str(tag) for tag in tags.sys_tags()],
    },
    sys.stdout,
)
"""


@lru_cache
def get_python_environment_and_tags(python: str) -> tuple[Environment, list[Tag]]:
    """Get target python Environment and tags.

    Run in a subprocess where packaging is installed.
    """
    with TemporaryDirectory() as packaging_install_dir:
        # first install packaging
        check_call(
            [
                *get_pip_command(python),
                "-q",
                "install",
                "--target",
                packaging_install_dir,
                "packaging",
            ]
        )
        res = check_output(
            [python, "-c", _SCRIPT],
            env=dict(os.environ, PYTHONPATH=packaging_install_dir),
        )
        res = json.loads(res)
        return cast("Environment", res["environment"]), [
            next(iter(parse_tag(tag))) for tag in res["tags"]
        ]
