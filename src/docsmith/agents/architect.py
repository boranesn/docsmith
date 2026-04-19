"""Architect agent: infer architecture, map modules, summarize design via Claude."""

from pathlib import Path

import anthropic

from docsmith.agents.state import DocsmithState
from docsmith.analysis.dependency import build_dependency_graph
from docsmith.config import settings
from docsmith.ingestion.walker import iter_source_files


def architect_agent(state: DocsmithState) -> dict:
    repo = state["repo_path"]
    source_files = list(iter_source_files(repo))
    module_graph = build_dependency_graph(Path(repo), source_files)

    functions = state.get("parsed_functions", [])
    classes = state.get("parsed_classes", [])

    symbol_summary = _build_symbol_summary(functions, classes)
    lang_breakdown = state.get("language_breakdown", {})

    prompt = f"""You are a software architect. Analyze this repository and produce a concise architecture summary.

Repository: {repo}
Languages: {lang_breakdown}
Entry points: {state.get('entry_points', [])}

Public functions ({len(functions)}):
{symbol_summary[:3000]}

Write a clear architecture summary covering:
1. Purpose and domain of the project
2. Main components and their responsibilities
3. Data flow between components
4. Key design patterns used
Keep it under 500 words."""

    summary = _call_claude(prompt)

    return {
        "module_graph": module_graph,
        "architecture_summary": summary,
        "agent_trace": state.get("agent_trace", []) + ["architect"],
    }


def _build_symbol_summary(functions, classes) -> str:
    lines = []
    for fn in functions[:50]:
        lines.append(f"  fn {fn.signature} [{fn.file_path}]")
    for cls in classes[:20]:
        lines.append(f"  class {cls.name} [{cls.file_path}]")
    return "\n".join(lines)


def _call_claude(prompt: str) -> str:
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text  # type: ignore[index]
    except Exception as e:
        return f"Architecture analysis unavailable: {e}"
