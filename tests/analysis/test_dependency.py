from pathlib import Path

import pytest

from docsmith.analysis.dependency import build_dependency_graph, to_mermaid


def test_build_dependency_graph(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("import os\nfrom pathlib import Path\n")
    (tmp_path / "utils.py").write_text("import json\n")

    files = [tmp_path / "main.py", tmp_path / "utils.py"]
    graph = build_dependency_graph(tmp_path, files)

    assert "main" in graph
    assert "utils" in graph
    assert "os" in graph["main"] or "pathlib" in graph["main"]


def test_to_mermaid_produces_valid_output() -> None:
    graph = {"app.routes": ["services.user", "services.auth"], "services.user": ["db.models"]}
    diagram = to_mermaid(graph)

    assert diagram.startswith("graph TD")
    assert "app_routes" in diagram
    assert "services_user" in diagram


def test_empty_graph() -> None:
    diagram = to_mermaid({})
    assert "graph TD" in diagram
