from typing import Set

from .compat import resource_as_file, resource_files
from .req_parser import canonicalize_name
from .utils import check_output


def list_depends(python: str, project_name: str) -> Set[str]:
    """List dependencies of an installed project.

    Return canonicalized distribution names, excluding the project
    itself.
    """
    with resource_as_file(
        resource_files("pip_deepfreeze").joinpath(  # type: ignore
            "list_depends_script.py"
        )
    ) as list_depends_script:
        dependencies = check_output(
            [python, str(list_depends_script), project_name]
        ).splitlines()
    return {canonicalize_name(d) for d in dependencies}
