from abc import ABC, abstractproperty
from typing import Any, Dict, List, Optional

from packaging.requirements import Requirement
from packaging.utils import NormalizedName, canonicalize_name


class DirectUrl:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def __str__(self) -> str:
        url = self.data.get("url")
        vcs_info = self.data.get("vcs_info")
        if vcs_info:
            vcs = vcs_info.get("vcs")
            commit_id = vcs_info.get("commit_id")
            return f"{vcs}+{url}@{commit_id}"
        else:
            return str(url)


class InstalledDistribution(ABC):
    """Abstract class for an installed distribution."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @property
    def name(self) -> NormalizedName:
        return canonicalize_name(self.data["metadata"]["name"])

    @property
    def version(self) -> str:
        version = self.data["metadata"]["version"]
        assert isinstance(version, str)
        return version

    @property
    def direct_url(self) -> Optional[DirectUrl]:
        direct_url = self.data.get("direct_url")
        if direct_url is None:
            return None
        return DirectUrl(direct_url)

    @property
    def requires_dist(self) -> List[Requirement]:
        """Requires-Dist metadata."""
        return [Requirement(r) for r in self.data["metadata"].get("requires_dist", [])]

    @abstractproperty
    def requires(self) -> List[Requirement]:
        """Base dependencies, filtered for the environment."""
        ...

    @abstractproperty
    def extra_requires(self) -> Dict[NormalizedName, List[Requirement]]:
        """Extra dependencies, filtered for the environment."""
        ...


class EnvInfoInstalledDistribution(InstalledDistribution):
    """An InstalledDistribution built from env_info_json.py output."""

    @property
    def requires(self) -> List[Requirement]:
        return [Requirement(req) for req in self.data.get("requires", [])]

    @property
    def extra_requires(self) -> Dict[NormalizedName, List[Requirement]]:
        return {
            canonicalize_name(extra): [Requirement(req) for req in reqs]
            for extra, reqs in self.data.get("extra_requires", {}).items()
        }


class PipInspectInstalledDistribution(InstalledDistribution):
    """An InstalledDistribution built from pip inspect output."""

    def __init__(self, data: Dict[str, Any], environment: Dict[str, str]):
        super().__init__(data)
        self.environment = environment

    @property
    def requires(self) -> List[Requirement]:
        return [
            req
            for req in self.requires_dist
            if req.marker is None or req.marker.evaluate(self.environment)
        ]

    @property
    def extra_requires(self) -> Dict[NormalizedName, List[Requirement]]:
        return {
            canonicalize_name(extra): [
                req
                for req in self.requires_dist
                if req.marker is not None
                and req.marker.evaluate(dict(self.environment, extra=extra))
            ]
            for extra in self.data["metadata"].get("provides_extra", [])
        }


InstalledDistributions = Dict[NormalizedName, InstalledDistribution]
