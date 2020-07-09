from pep517.meta import load as load_metadata  # type: ignore


def get_project_name(root: str = ".") -> str:
    distribution = load_metadata(root)
    return str(distribution.metadata["Name"])
