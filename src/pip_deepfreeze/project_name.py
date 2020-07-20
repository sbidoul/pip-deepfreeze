import os
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

from .utils import check_call, check_output, log_info


@lru_cache(maxsize=1)
def get_project_name(python: str, project_root: Path) -> str:
    """Get a project name building metadata using pep517.

    We build in a separate process so we support python 2 builds.
    """
    with TemporaryDirectory() as pep517_install_dir:
        log_info("Getting project metadata..", nl=False)
        # first install pep517
        check_call(
            [
                python,
                "-m",
                "pip",
                "-q",
                "install",
                "--target",
                pep517_install_dir,
                "pep517==0.8.2",
            ]
        )
        log_info(".", nl=False)
        # TODO this uses an undocumented function of pep517
        name = check_output(
            [
                python,
                "-c",
                "from pep517.meta import load; import sys; "
                "sys.stdout.write(load(sys.argv[1]).metadata['Name'])",
                str(project_root),
            ],
            env=dict(os.environ, PYTHONPATH=pep517_install_dir),
        )
        log_info(" " + name)
        return name
