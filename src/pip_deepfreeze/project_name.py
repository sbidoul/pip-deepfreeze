from functools import lru_cache

from pep517.meta import load as load_metadata  # type: ignore


@lru_cache(maxsize=1)
def get_project_name(root: str = ".") -> str:
    distribution = load_metadata(root)
    return str(distribution.metadata["Name"])
