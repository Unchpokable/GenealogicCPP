from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text
from rich.tree import Tree

from .tree import TreeNode, count_nodes

console = Console()


def make_progress() -> Progress:
    """Create a Rich Progress bar for file scanning."""
    return Progress(
        SpinnerColumn("dots"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )


def print_header(base_class: str, directory: Path, ext: str) -> None:
    header = Text.assemble(
        ("Genealogic", "bold magenta"),
        (" - C++ Inheritance Tree Visualizer\n\n", "dim"),
        ("  Base class:  ", "dim"),
        (base_class, "bold cyan"),
        ("\n"),
        ("  Directory:   ", "dim"),
        (str(directory), "bold"),
        ("\n"),
        ("  Extension:   ", "dim"),
        (ext, "bold"),
    )
    console.print(Panel(header, border_style="blue", padding=(1, 2)))


def print_scan_result(total_files: int, total_pairs: int) -> None:
    console.print(
        f"  [dim]Scanned[/] [bold]{total_files}[/] [dim]files,[/] "
        f"[dim]found[/] [bold]{total_pairs}[/] [dim]inheritance relationships[/]"
    )


def print_tree_preview(
    root: TreeNode,
    parents_map: dict[str, list[str]] | None = None,
) -> None:
    """Print a Rich Tree widget as a console preview with multi-parent annotations."""
    total = count_nodes(root)
    console.print()
    console.print(f"  [dim]Inheritance tree:[/] [bold]{total}[/] [dim]classes[/]")
    console.print()

    rich_tree = Tree(f"[bold cyan]{root.name}[/]", guide_style="blue")
    _build_rich_tree(rich_tree, root, root.name, parents_map)
    console.print(rich_tree)
    console.print()


def _format_node_label(
    node_name: str,
    tree_parent_name: str,
    parents_map: dict[str, list[str]] | None,
) -> str:
    """Format a node label, showing extra parents if multiple inheritance."""
    if not parents_map:
        return f"[white]{node_name}[/]"

    all_parents = parents_map.get(node_name, [])
    extra = [p for p in all_parents if p != tree_parent_name]

    if extra:
        extra_str = ", ".join(extra)
        return f"[white]{node_name}[/] [dim](+ {extra_str})[/]"

    return f"[white]{node_name}[/]"


def _build_rich_tree(
    rich_node: Tree,
    tree_node: TreeNode,
    parent_name: str,
    parents_map: dict[str, list[str]] | None,
) -> None:
    for child in tree_node.children:
        label = _format_node_label(child.name, parent_name, parents_map)
        branch = rich_node.add(label)
        _build_rich_tree(branch, child, child.name, parents_map)


def print_output_info(output_path: Path) -> None:
    console.print(
        f"  [bold green]\u2713[/] [dim]Rendered to[/] [bold]{output_path}[/]"
    )
    console.print()


def print_error(msg: str) -> None:
    console.print(f"  [bold red]\u2717[/] {msg}")


def print_warning(msg: str) -> None:
    console.print(f"  [bold yellow]![/] {msg}")
