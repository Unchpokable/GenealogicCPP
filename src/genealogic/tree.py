from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class TreeNode:
    name: str
    children: list[TreeNode] = field(default_factory=list)


def build_children_map(
    pairs: list[tuple[str, str]],
) -> dict[str, list[str]]:
    """Build a mapping from parent class name to list of child class names."""
    children_map: dict[str, list[str]] = defaultdict(list)
    for child, parent in pairs:
        children_map[parent].append(child)
    return children_map


def build_tree(root_name: str, children_map: dict[str, list[str]]) -> TreeNode:
    """BFS from root_name to build a TreeNode tree."""
    root = TreeNode(name=root_name)
    queue: deque[TreeNode] = deque([root])
    visited: set[str] = {root_name}

    while queue:
        node = queue.popleft()
        for child_name in sorted(children_map.get(node.name, [])):
            if child_name in visited:
                continue
            visited.add(child_name)
            child_node = TreeNode(name=child_name)
            node.children.append(child_node)
            queue.append(child_node)

    return root


def count_nodes(node: TreeNode) -> int:
    """Count total nodes in the tree."""
    total = 1
    for child in node.children:
        total += count_nodes(child)
    return total
