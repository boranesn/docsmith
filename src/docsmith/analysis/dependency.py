"""Build module import dependency graph from Python source files."""

import ast
from pathlib import Path


def build_dependency_graph(repo_root: Path, source_files: list[Path]) -> dict[str, list[str]]:
    """Return {module: [imported_modules]} for all Python files."""
    root_str = str(repo_root)
    graph: dict[str, list[str]] = {}

    for path in source_files:
        if path.suffix != ".py":
            continue
        mod_name = _path_to_module(path, repo_root)
        imports = _extract_imports(path)
        graph[mod_name] = imports

    return graph


def _path_to_module(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    return str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")


def _extract_imports(path: Path) -> list[str]:
    try:
        source = path.read_text(errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return list(set(imports))


def to_mermaid(graph: dict[str, list[str]]) -> str:
    lines = ["graph TD"]
    seen: set[str] = set()
    for src, targets in graph.items():
        src_id = src.replace(".", "_")
        for tgt in targets:
            tgt_id = tgt.replace(".", "_")
            edge = f"    {src_id} --> {tgt_id}"
            if edge not in seen:
                lines.append(edge)
                seen.add(edge)
    return "\n".join(lines)
