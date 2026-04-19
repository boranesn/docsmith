from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from docsmith.agents.state import DocsmithState


def _base_state(repo: str = "/tmp/repo") -> DocsmithState:
    return DocsmithState(
        repo_path=repo,
        output_path="/tmp/docs",
        changed_files=set(),
        language_breakdown={},
        entry_points=[],
        parsed_functions=[],
        parsed_classes=[],
        module_graph={},
        architecture_summary="",
        api_pages=[],
        guide_pages=[],
        diagrams=[],
        review_notes=[],
        quality_score=0.0,
        retry_count=0,
        agent_trace=[],
        coverage=None,
        messages=[],
    )


def test_explorer_agent_language_breakdown(tmp_path: Path) -> None:
    from docsmith.agents.explorer import explorer_agent

    (tmp_path / "app.py").write_text("pass")
    (tmp_path / "utils.py").write_text("pass")
    (tmp_path / "index.ts").write_text("export const x = 1;")

    state = _base_state(str(tmp_path))
    result = explorer_agent(state)

    assert "python" in result["language_breakdown"]
    assert "explorer" in result["agent_trace"]


def test_reviewer_scores_empty_state() -> None:
    from docsmith.agents.reviewer import reviewer_agent

    state = _base_state()
    result = reviewer_agent(state)

    assert 0.0 <= result["quality_score"] <= 1.0
    assert "reviewer" in result["agent_trace"]
    assert result["coverage"] is not None


def test_should_retry_logic() -> None:
    from docsmith.agents.reviewer import should_retry

    low_quality = _base_state()
    low_quality["quality_score"] = 0.3
    low_quality["retry_count"] = 0
    assert should_retry(low_quality) == "retry"

    max_retries = _base_state()
    max_retries["quality_score"] = 0.3
    max_retries["retry_count"] = 3
    assert should_retry(max_retries) == "end"

    high_quality = _base_state()
    high_quality["quality_score"] = 0.9
    high_quality["retry_count"] = 0
    assert should_retry(high_quality) == "end"
