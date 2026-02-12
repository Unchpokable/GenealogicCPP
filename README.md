# Genealogic

C++ class inheritance tree visualizer. Parses header files, builds a class hierarchy from a given base class, and renders it as a graph image.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [Graphviz](https://graphviz.org/download/) (`dot` must be in PATH) — for image rendering

## Installation

```bash
git clone https://github.com/Unchpokable/GenealogicCPP.git
cd GenealogicCPP
uv sync
```

## Usage

```bash
uv run genealogic <base_class> <directory> [options]
```

### Arguments

| Argument     | Description                        |
|--------------|------------------------------------|
| `base_class` | Root class name to start the tree  |
| `directory`  | Path to C++ source directory       |

### Options

| Option             | Description                                      | Default |
|--------------------|--------------------------------------------------|---------|
| `-e`, `--ext`      | Header file extension filter                     | `.h`    |
| `-o`, `--output`   | Output directory for the rendered image           | `.`     |
| `-f`, `--format`   | Output format: `svg`, `png`, `pdf`               | `svg`   |
| `--single-class`   | 1-header-1-class optimization (read first N lines)| off    |
| `--max-lines`      | Max lines to read in single-class mode           | `100`   |
| `--no-open`        | Don't auto-open the result                       | off     |

### Examples

```bash
# Basic usage
uv run genealogic Animal src/include

# Custom extension and output directory
uv run genealogic BaseWidget src/widgets -e .hpp -o ./output

# PNG output with single-class optimization
uv run genealogic IComponent engine/headers -e .hxx -f png --single-class
```

If Graphviz is not installed, the tree will still be displayed in the console as a text preview.
