from typing import Dict, Optional, Sequence, Set

from packaging.requirements import Requirement
from packaging.utils import NormalizedName, canonicalize_name

from .installed_dist import InstalledDistributions
from .utils import make_project_name_with_extras


def list_installed_depends(
    installed_dists: InstalledDistributions,
    project_name: NormalizedName,
    extras: Optional[Sequence[NormalizedName]] = None,
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
                extra = canonicalize_name(extra)
                if extra not in dist.extra_requires:
                    # extra is not a known extra of installed dist,
                    # so we can't report it's dependencies
                    continue
                for dep_req in dist.extra_requires[extra]:
                    add(dep_req, deps_only=False)

    add(
        Requirement(make_project_name_with_extras(project_name, extras)),
        deps_only=True,
    )

    return res


def list_installed_depends_by_extra(
    installed_dists: InstalledDistributions,
    project_name: NormalizedName,
) -> Dict[Optional[NormalizedName], Set[NormalizedName]]:
    """Get installed dependencies of a project, grouped by extra."""
    res = {}  # type: Dict[Optional[NormalizedName], Set[NormalizedName]]
    base_depends = list_installed_depends(installed_dists, project_name)
    res[None] = base_depends
    for extra in installed_dists[project_name].extra_requires:
        extra_depends = list_installed_depends(installed_dists, project_name, [extra])
        res[extra] = extra_depends - base_depends
    return res
