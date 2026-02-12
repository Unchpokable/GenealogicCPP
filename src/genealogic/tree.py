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
        if child not in children_map[parent]:
            children_map[parent].append(child)
    return children_map


def build_parents_map(
    pairs: list[tuple[str, str]],
) -> dict[str, list[str]]:
    """Build a reverse mapping: child class -> list of parent class names."""
    parents_map: dict[str, list[str]] = defaultdict(list)
    for child, parent in pairs:
        if parent not in parents_map[child]:
            parents_map[child].append(parent)
    return parents_map


def build_tree(root_name: str, children_map: dict[str, list[str]]) -> TreeNode:
    """BFS from root_name to build a TreeNode tree (each node appears once)."""
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


def collect_reachable_edges(
    root_name: str,
    children_map: dict[str, list[str]],
) -> tuple[set[str], list[tuple[str, str]]]:
    """BFS from root. Return (all_node_names, all_edges) as a full DAG."""
    nodes: set[str] = {root_name}
    edges: list[tuple[str, str]] = []
    queue: deque[str] = deque([root_name])

    while queue:
        parent = queue.popleft()
        for child in sorted(children_map.get(parent, [])):
            edges.append((parent, child))
            if child not in nodes:
                nodes.add(child)
                queue.append(child)

    return nodes, edges


def count_nodes(node: TreeNode) -> int:
    """Count total nodes in the tree."""
    total = 1
    for child in node.children:
        total += count_nodes(child)
    return total
