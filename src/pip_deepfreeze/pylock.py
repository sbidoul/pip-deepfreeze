from collections.abc import Iterable, Iterator
from pathlib import Path

from packaging.pylock import (
    Package,
    PackageArchive,
    PackageDirectory,
    PackageSdist,
    PackageVcs,
    PackageWheel,
    Pylock,
)

from .compat import tomllib
from .python_env import get_python_environment_and_tags


def _dist_url(dist: PackageArchive | PackageVcs) -> str:
    if dist.path:
        return Path(dist.path).absolute().as_uri()
    elif dist.url:
        return dist.url
    else:
        raise ValueError("Distribution must have either a path or URL.")


def _package_vcs_url(dist: PackageVcs) -> str:
    url = f"{dist.type}+{_dist_url(dist)}@{dist.commit_id}"
    if dist.subdirectory:
        url += f"#subdirectory={dist.subdirectory}"
    return url


def _pylock_packages_to_requirements(
    packages: Iterable[
        tuple[
            Package,
            PackageArchive
            | PackageSdist
            | PackageWheel
            | PackageVcs
            | PackageDirectory,
        ]
    ],
) -> Iterator[str]:
    for package, package_dist in packages:
        if isinstance(package_dist, PackageWheel):
            yield f"{package.name}=={package.version}"
        elif isinstance(package_dist, PackageSdist):
            yield f"{package.name}=={package.version}"
        elif isinstance(package_dist, PackageVcs):
            yield f"{package.name} @ {_package_vcs_url(package_dist)}"
        elif isinstance(package_dist, PackageArchive):
            yield f"{package.name} @ {_dist_url(package_dist)}"
        elif isinstance(package_dist, PackageDirectory):
            yield f"{'-e ' if package_dist.editable else ''}{package_dist.path}"
        else:
            raise NotImplementedError(
                f"Unsupported package distribution type: {type(package_dist)}"
            )


def pylock_to_requirements_txt(
    python: str,
    pylock_path: Path,
    requirements_txt_path: Path,
) -> None:
    """Convert a pylock.toml file to a requirements.txt string.

    This selects for all extras and dependency groups.
    """
    if not pylock_path.is_file():
        requirements = ""
    else:
        environment, tags = get_python_environment_and_tags(python)
        pylock = Pylock.from_dict(
            tomllib.loads(pylock_path.read_text(encoding="utf-8"))
        )
        requirements = "\n".join(
            _pylock_packages_to_requirements(
                pylock.select(
                    environment=environment,
                    tags=tags,
                    extras=pylock.extras,
                    dependency_groups=pylock.dependency_groups,
                )
            )
        )
    requirements_txt_path.write_text(requirements)
