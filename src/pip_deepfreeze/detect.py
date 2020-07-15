from pathlib import Path


def supports_editable(root: Path = Path(".")) -> bool:
    return (root / "setup.py").is_file()
