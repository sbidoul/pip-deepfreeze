from typing import List


def split_lines(s: str) -> List[str]:
    s = s.strip()
    if not s:
        return []
    return s.split("\n")
