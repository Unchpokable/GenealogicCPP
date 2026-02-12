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


def _extract_template_args(template_str: str) -> list[str]:
    """Extract plain identifiers from template arguments like '<Feature, Object>'.

    Skips nested templates and non-identifier tokens (e.g. int, std::string).
    """
    # Strip outer < >
    inner = template_str.strip()
    if inner.startswith("<") and inner.endswith(">"):
        inner = inner[1:-1]

    args: list[str] = []
    depth = 0
    current: list[str] = []

    for ch in inner:
        if ch == "<":
            depth += 1
            current.append(ch)
        elif ch == ">":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

    tail = "".join(current).strip()
    if tail:
        args.append(tail)

    # Keep only plain identifiers that look like class names (start with uppercase)
    names: list[str] = []
    for arg in args:
        m = re.match(r"^(\w+)$", arg.strip())
        if m and m.group(1)[0].isupper():
            names.append(m.group(1))

    return names


def _extract_base_names(segment: str, child_name: str) -> list[str]:
    """Extract base class names from a segment like 'virtual public Base<T, Parent>'.

    Returns the template class name itself, plus any template arguments
    that look like class names (uppercase start), excluding the child class itself.
    """
    tokens = segment.split()
    filtered = [t for t in tokens if t not in _ACCESS_SPECIFIERS]
    if not filtered:
        return []

    name_part = " ".join(filtered)

    # Extract the main class name (before '<')
    m = re.match(r"(\w+)", name_part)
    if not m:
        return []

    names: list[str] = [m.group(1)]

    # Extract template arguments as potential parents
    tmpl_match = re.search(r"(<.+>)", name_part, re.DOTALL)
    if tmpl_match:
        for arg_name in _extract_template_args(tmpl_match.group(1)):
            if arg_name != child_name and arg_name not in names:
                names.append(arg_name)

    return names


def parse_declarations(text: str) -> list[tuple[str, str]]:
    """Parse all class/struct inheritance declarations from text.

    Returns list of (child_class, base_class) pairs.
    One declaration can yield multiple pairs (multiple inheritance).
    Template arguments of base classes that look like class names
    are also included as parents (e.g. StaticObjectInterface<Self, Object>
    yields both StaticObjectInterface and Object as parents).
    """
    results: list[tuple[str, str]] = []

    for match in DECL_RE.finditer(text):
        child_name = match.group(1)
        raw_bases = match.group(2)

        for segment in _split_base_list(raw_bases):
            for base_name in _extract_base_names(segment, child_name):
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
