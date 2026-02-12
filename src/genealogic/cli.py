import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="genealogic",
        description="C++ class inheritance tree visualizer",
    )

    parser.add_argument(
        "base_class",
        help="Root base class name to start the tree from",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Path to the C++ source directory",
    )

    parser.add_argument(
        "-e", "--ext",
        default=".h",
        help="Header file extension filter (default: .h)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory for the rendered image (default: current directory)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["svg", "png", "pdf"],
        default="svg",
        help="Output format (default: svg)",
    )
    parser.add_argument(
        "--single-class",
        action="store_true",
        help="Optimize for 1-header-1-class: read only first N lines per file",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=100,
        help="Max lines to read in single-class mode (default: 100)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't auto-open the result after rendering",
    )

    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        parser.error(f"Directory not found: {args.directory}")

    ext = args.ext if args.ext.startswith(".") else f".{args.ext}"
    args.ext = ext

    output_dir = args.output if args.output else Path.cwd()
    if not output_dir.is_dir():
        parser.error(f"Output directory not found: {output_dir}")
    args.output = output_dir / f"{args.base_class}_inheritance.{args.format}"

    return args
