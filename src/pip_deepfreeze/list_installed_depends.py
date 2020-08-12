from typing import Iterable, Optional, Set

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from .compat import NormalizedName
from .installed_dist import InstalledDistributions


def list_installed_depends(
    installed_dists: InstalledDistributions,
    project_name: NormalizedName,
    extras: Optional[Iterable[NormalizedName]] = None,
) -> Set[NormalizedName]:
    """List installed dependencies of an installed project.

    Return canonicalized distribution names, excluding the project
    itself.
    """
    res = set()
    seen = set()

    def add(req: Requirement, deps_only: bool) -> None:
        req_name = canonicalize_name(req.name)
        seen_key = (req_name, tuple(sorted(req.extras)))
        if seen_key in seen:
            return
        seen.add(seen_key)
        try:
            dist = installed_dists[req_name]
        except KeyError:
            # not installed
            return
        else:
            if not deps_only:
                res.add(req_name)
            for dep_req in dist.requires:
                add(dep_req, deps_only=False)
            for extra in req.extras:
                for dep_req in dist.extra_requires[extra]:
                    add(dep_req, deps_only=False)

    project_name_with_extras = str(project_name)
    if extras:
        project_name_with_extras += "[" + ",".join(extras) + "]"
    add(
        Requirement(project_name_with_extras), deps_only=True,
    )

    return res
