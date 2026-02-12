import asyncio
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from .cli import parse_args
from .parser import collect_headers, parse_file
from .tree import build_children_map, build_tree
from .tui import (
    console,
    make_progress,
    print_error,
    print_header,
    print_output_info,
    print_scan_result,
    print_tree_preview,
    print_warning,
)
from .visualizer import render_tree


async def scan_files(
    headers: list[Path],
    single_class: bool,
    max_lines: int,
) -> list[tuple[str, str]]:
    """Scan all header files asynchronously with a progress bar."""
    all_pairs: list[tuple[str, str]] = []

    progress = make_progress()
    with progress:
        task = progress.add_task("Scanning headers...", total=len(headers))

        semaphore = asyncio.Semaphore(64)

        async def process_one(filepath: Path) -> list[tuple[str, str]]:
            async with semaphore:
                result = await parse_file(filepath, single_class, max_lines)
                progress.advance(task)
                return result

        tasks = [process_one(h) for h in headers]
        results = await asyncio.gather(*tasks)

    for pairs in results:
        all_pairs.extend(pairs)

    return all_pairs


def open_file(path: Path) -> None:
    """Open a file with the default system application."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(path))
        elif system == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except OSError:
        pass


def run() -> int:
    args = parse_args()

    print_header(args.base_class, args.directory, args.ext)

    has_dot = shutil.which("dot") is not None
    if not has_dot:
        print_warning(
            "Graphviz 'dot' not found in PATH. "
            "Tree will be shown in console only. "
            "Install Graphviz to render image output."
        )

    headers = collect_headers(args.directory, args.ext)
    if not headers:
        print_error(f"No *{args.ext} files found in {args.directory}")
        return 1

    console.print(f"  [dim]Found[/] [bold]{len(headers)}[/] [dim]header files[/]")
    console.print()

    all_pairs = asyncio.run(
        scan_files(headers, args.single_class, args.max_lines)
    )
    print_scan_result(len(headers), len(all_pairs))

    children_map = build_children_map(all_pairs)

    if args.base_class not in children_map:
        has_as_child = any(args.base_class == child for child, _ in all_pairs)
        if not has_as_child:
            print_error(
                f"Class '{args.base_class}' not found in any inheritance relationship"
            )
            return 1

    with console.status("[bold blue]Building inheritance tree...", spinner="dots"):
        root = build_tree(args.base_class, children_map)

    if not root.children:
        print_warning(f"No classes inherit from '{args.base_class}'")
        return 0

    print_tree_preview(root)

    if has_dot:
        with console.status("[bold blue]Rendering graph...", spinner="dots"):
            output_path = render_tree(root, str(args.output), args.format)

        print_output_info(output_path)

        if not args.no_open:
            open_file(output_path)
    else:
        print_warning("Skipping image rendering (Graphviz not installed)")

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
