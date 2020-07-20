from typing import Set

from .compat import resource_as_file, resource_files
from .req_parser import canonicalize_name
from .utils import check_output, split_lines


def list_depends(python: str, project_name: str) -> Set[str]:
    with resource_as_file(
        resource_files("pip_deepfreeze").joinpath(  # type: ignore
            "list_depends_script.py"
        )
    ) as list_depends_script:
        # str(list_depends_script) seems necessary for python 3.6 compatibility
        # on Winwdows.
        dependencies = split_lines(
            check_output([python, str(list_depends_script), project_name])
        )
    return {canonicalize_name(d) for d in dependencies}
