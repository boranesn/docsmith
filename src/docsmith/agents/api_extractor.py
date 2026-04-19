"""API Extractor agent: parse all public functions and classes from AST."""

from pathlib import Path

from docsmith.agents.state import DocsmithState
from docsmith.analysis.complexity import annotate_complexity
from docsmith.ingestion.parser import parse_file
from docsmith.ingestion.walker import iter_source_files
from docsmith.models import ParsedClass, ParsedFunction


def api_extractor_agent(state: DocsmithState) -> dict:
    repo = state["repo_path"]
    changed = state.get("changed_files") or set()

    all_functions: list[ParsedFunction] = []
    all_classes: list[ParsedClass] = []

    source_files = list(iter_source_files(repo, include_languages={"python", "typescript", "javascript"}))
    if changed:
        source_files = [f for f in source_files if str(f) in changed]

    for path in source_files:
        fns, cls = parse_file(path)
        lines = path.read_text(errors="replace").splitlines()
        fns = annotate_complexity(fns, lines)
        all_functions.extend(fns)
        all_classes.extend(cls)

    return {
        "parsed_functions": all_functions,
        "parsed_classes": all_classes,
        "agent_trace": state.get("agent_trace", []) + ["api_extractor"],
    }
