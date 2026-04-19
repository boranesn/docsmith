"""Render dependency graphs as Mermaid diagram strings."""

from docsmith.analysis.dependency import to_mermaid


def render_mermaid(module_graph: dict[str, list[str]]) -> str:
    return to_mermaid(module_graph)


def wrap_html(mermaid_src: str, title: str = "Diagram") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
  <div class="mermaid">
{mermaid_src}
  </div>
  <script>mermaid.initialize({{startOnLoad: true}});</script>
</body>
</html>"""
