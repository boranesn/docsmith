"""Explorer agent: understand repo structure, detect languages, find entry points."""

from collections import Counter
from pathlib import Path

from docsmith.agents.state import DocsmithState
from docsmith.ingestion.languages import detect_language
from docsmith.ingestion.walker import iter_source_files


_ENTRY_POINT_NAMES = {
    "main.py", "app.py", "server.py", "index.py", "cli.py",
    "manage.py", "wsgi.py", "asgi.py", "index.ts", "index.js",
    "main.ts", "main.go", "main.rs",
}


def explorer_agent(state: DocsmithState) -> dict:
    repo = state["repo_path"]
    changed = state.get("changed_files") or set()

    files = list(iter_source_files(repo))
    lang_counter: Counter[str] = Counter()
    entry_points: list[str] = []

    for path in files:
        lang = detect_language(path)
        if lang:
            lang_counter[lang] += 1
        if path.name in _ENTRY_POINT_NAMES:
            entry_points.append(str(path))

    return {
        "language_breakdown": dict(lang_counter),
        "entry_points": entry_points,
        "agent_trace": state.get("agent_trace", []) + ["explorer"],
    }
