"""Reviewer agent: quality-check consistency and coverage, assign quality score."""

import anthropic

from docsmith.agents.state import DocsmithState
from docsmith.analysis.coverage import compute_coverage
from docsmith.config import settings
from docsmith.models import DocPage


def reviewer_agent(state: DocsmithState) -> dict:
    api_pages = state.get("api_pages", [])
    guide_pages = state.get("guide_pages", [])
    functions = state.get("parsed_functions", [])
    classes = state.get("parsed_classes", [])
    arch = state.get("architecture_summary", "")
    retry_count = state.get("retry_count", 0)

    coverage = compute_coverage(functions, classes)
    notes: list[str] = []
    score = 0.0

    # Score components
    if guide_pages:
        score += 0.3
    if api_pages:
        score += 0.25
    if state.get("diagrams"):
        score += 0.15
    if arch:
        score += 0.15
    score += min(0.15, coverage.coverage_pct / 100 * 0.15)

    if coverage.coverage_pct < 50:
        notes.append(f"Low docstring coverage: {coverage.coverage_pct:.1f}%")
    if not state.get("diagrams"):
        notes.append("No architecture diagrams generated")

    all_pages = guide_pages + api_pages
    if all_pages and arch:
        llm_notes = _llm_review(all_pages, arch)
        notes.extend(llm_notes)

    return {
        "coverage": coverage,
        "quality_score": round(score, 2),
        "review_notes": notes,
        "retry_count": retry_count,
        "agent_trace": state.get("agent_trace", []) + ["reviewer"],
    }


def _llm_review(pages: list[DocPage], arch: str) -> list[str]:
    page_sample = "\n---\n".join(p.content[:500] for p in pages[:3])
    prompt = f"""Review this documentation for quality issues. Be brief and specific.

Architecture summary:
{arch[:800]}

Documentation sample:
{page_sample[:1500]}

List up to 5 specific issues (missing info, inconsistencies, unclear sections).
If quality is good, respond: "No major issues found."
Each issue on a new line starting with "- "."""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text  # type: ignore[index]
        return [line.lstrip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]
    except Exception:
        return []


def should_retry(state: DocsmithState) -> str:
    score = state.get("quality_score", 0.0)
    retry_count = state.get("retry_count", 0)
    if score < settings.quality_threshold and retry_count < settings.max_retries:
        return "retry"
    return "end"
