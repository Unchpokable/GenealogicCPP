from pathlib import Path

import graphviz


def render_graph(
    root_name: str,
    nodes: set[str],
    edges: list[tuple[str, str]],
    output_path: str,
    fmt: str = "svg",
) -> Path:
    """Render the inheritance DAG to an image file using Graphviz."""
    dot = graphviz.Digraph(
        name="InheritanceTree",
        format=fmt,
        graph_attr={
            "rankdir": "TB",
            "splines": "ortho",
            "nodesep": "0.6",
            "ranksep": "0.8",
            "bgcolor": "#1e1e2e",
            "pad": "0.5",
        },
        node_attr={
            "shape": "record",
            "style": "filled,rounded",
            "fillcolor": "#313244",
            "fontcolor": "#cdd6f4",
            "fontname": "Consolas",
            "fontsize": "11",
            "color": "#585b70",
            "penwidth": "1.5",
        },
        edge_attr={
            "color": "#89b4fa",
            "arrowhead": "vee",
            "arrowsize": "0.8",
            "penwidth": "1.2",
        },
    )

    for name in sorted(nodes):
        attrs = {}
        if name == root_name:
            attrs = {
                "fillcolor": "#89b4fa",
                "fontcolor": "#1e1e2e",
                "penwidth": "2.5",
                "color": "#74c7ec",
            }
        dot.node(name, name, **attrs)

    for parent, child in edges:
        dot.edge(parent, child)

    out = Path(output_path)
    stem = str(out.with_suffix(""))
    dot.render(stem, cleanup=True)
    return out
