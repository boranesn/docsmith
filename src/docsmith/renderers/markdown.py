"""Render agent output to Markdown files on disk."""

from pathlib import Path

from docsmith.models import DocPage


def render_docs(state: dict, output_path: Path) -> None:
    output_path.mkdir(parents=True, exist_ok=True)

    all_pages: list[DocPage] = state.get("guide_pages", []) + state.get("api_pages", [])
    for page in all_pages:
        dest = output_path / page.filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page.content, encoding="utf-8")

    diagrams = state.get("diagrams", [])
    if diagrams:
        diag_dir = output_path / "diagrams"
        diag_dir.mkdir(parents=True, exist_ok=True)
        for i, diagram in enumerate(diagrams):
            name = "dependency" if i == 0 else f"diagram-{i}"
            (diag_dir / f"{name}.mermaid").write_text(diagram, encoding="utf-8")

    _write_metadata(state, output_path)


def _write_metadata(state: dict, output_path: Path) -> None:
    import json
    from datetime import datetime

    coverage = state.get("coverage")
    meta = {
        "last_run": datetime.utcnow().isoformat(),
        "quality_score": state.get("quality_score", 0.0),
        "agent_trace": state.get("agent_trace", []),
        "language_breakdown": state.get("language_breakdown", {}),
        "coverage_pct": coverage.coverage_pct if coverage else None,
        "review_notes": state.get("review_notes", []),
    }
    (output_path / "docsmith.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
