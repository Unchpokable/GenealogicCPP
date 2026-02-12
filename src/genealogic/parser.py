import re
from pathlib import Path

import aiofiles

CLASS_INHERITANCE_RE = re.compile(
    r"^\s*class\s+"
    r"(?:[\w]+(?:\([^)]*\))?\s+)*?"  # optional declspec / export macros
    r"(\w+)\s*"                       # capture group 1: derived class name
    r"(?:final\s+)?"                  # optional 'final'
    r":\s*"
    r"(?:virtual\s+)?"               # optional 'virtual'
    r"(?:public|protected|private)\s+"
    r"(\w+)",                         # capture group 2: base class name
)


def parse_line(line: str) -> tuple[str, str] | None:
    """Try to extract (ChildClass, BaseClass) from a single line."""
    m = CLASS_INHERITANCE_RE.search(line)
    if m:
        return m.group(1), m.group(2)
    return None


async def parse_file(
    filepath: Path,
    single_class: bool = False,
    max_lines: int = 100,
) -> list[tuple[str, str]]:
    """Parse a header file and return list of (child, parent) pairs."""
    results: list[tuple[str, str]] = []
    try:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8", errors="replace") as f:
            line_no = 0
            async for line in f:
                pair = parse_line(line)
                if pair:
                    results.append(pair)
                    if single_class:
                        break
                line_no += 1
                if single_class and line_no >= max_lines:
                    break
    except (OSError, PermissionError):
        pass
    return results


def collect_headers(directory: Path, ext: str) -> list[Path]:
    """Recursively collect header files matching the given extension."""
    pattern = f"**/*{ext}"
    return sorted(directory.glob(pattern))
