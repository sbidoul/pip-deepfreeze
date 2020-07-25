from typing import Any, Dict, List

from packaging.requirements import Requirement

from .req_parser import canonicalize_name


class InstalledDistribution:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @property
    def name(self) -> str:
        return canonicalize_name(self.data["metadata"]["name"])

    @property
    def version(self) -> str:
        version = self.data["metadata"]["version"]
        assert isinstance(version, str)
        return version

    @property
    def requires_dist(self) -> List[Requirement]:
        return [Requirement(r) for r in self.data["metadata"].get("requires_dist", [])]

    @property
    def requires(self) -> List[Requirement]:
        return [Requirement(req) for req in self.data.get("requires", [])]

    @property
    def extra_requires(self) -> Dict[str, List[Requirement]]:
        return {
            extra: [Requirement(req) for req in reqs]
            for extra, reqs in self.data.get("extra_requires", {}).items()
        }


InstalledDistributions = Dict[str, InstalledDistribution]
