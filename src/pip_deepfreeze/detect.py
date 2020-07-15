from pathlib import Path


def supports_editable(project_root: Path = Path(".")) -> bool:
    return (project_root / "setup.py").is_file()
