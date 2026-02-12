import re
from pathlib import Path

import aiofiles

# Matches class/struct declarations with inheritance, spanning multiple lines.
# Group 1: derived class name
# Group 2: raw base class list (everything between ':' and '{')
DECL_RE = re.compile(
    r"(?:class|struct)\s+"
    r"(?:[\w]+(?:\([^)]*\))?\s+)*?"   # optional declspec / export macros
    r"(\w+)\s*"                         # group 1: class name
    r"(?:final\s*)?"                    # optional 'final'
    r":\s*"                             # colon before base list
    r"([^{;]+)"                         # group 2: base list (until '{' or ';')
    r"\{",
    re.DOTALL,
)

_ACCESS_SPECIFIERS = {"public", "protected", "private", "virtual"}


def _split_base_list(raw: str) -> list[str]:
    """Split a base class list by commas, respecting template <> nesting."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []

    for ch in raw:
        if ch == "<":
            depth += 1
            current.append(ch)
        elif ch == ">":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)

    return parts


def _extract_base_name(segment: str) -> str | None:
    """Extract the base class name from a segment like 'virtual public Base<T>'."""
    tokens = segment.split()
    # Filter out access specifiers and 'virtual'
    filtered = [t for t in tokens if t not in _ACCESS_SPECIFIERS]
    if not filtered:
        return None

    # The remaining part is something like 'Base<T>' or 'Base'
    name_part = " ".join(filtered)

    # Extract identifier before '<' (template) or take the whole word
    m = re.match(r"(\w+)", name_part)
    return m.group(1) if m else None


def parse_declarations(text: str) -> list[tuple[str, str]]:
    """Parse all class/struct inheritance declarations from text.

    Returns list of (child_class, base_class) pairs.
    One declaration can yield multiple pairs (multiple inheritance).
    """
    results: list[tuple[str, str]] = []

    for match in DECL_RE.finditer(text):
        child_name = match.group(1)
        raw_bases = match.group(2)

        for segment in _split_base_list(raw_bases):
            base_name = _extract_base_name(segment)
            if base_name:
                results.append((child_name, base_name))

    return results


async def parse_file(
    filepath: Path,
    single_class: bool = False,
    max_lines: int = 100,
) -> list[tuple[str, str]]:
    """Parse a header file and return list of (child, parent) pairs."""
    try:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8", errors="replace") as f:
            if single_class:
                lines: list[str] = []
                count = 0
                async for line in f:
                    lines.append(line)
                    count += 1
                    if count >= max_lines:
                        break
                text = "".join(lines)
            else:
                text = await f.read()
    except (OSError, PermissionError):
        return []

    return parse_declarations(text)


def collect_headers(directory: Path, ext: str) -> list[Path]:
    """Recursively collect header files matching the given extension."""
    pattern = f"**/*{ext}"
    return sorted(directory.glob(pattern))
