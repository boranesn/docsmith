from collections.abc import Iterator
from pathlib import Path

import pathspec

from docsmith.ingestion.languages import detect_language

_DEFAULT_IGNORES = [
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".eggs", "*.egg-info", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", ".docsmith", "*.min.js", "*.map",
]


def _load_gitignore(repo_root: Path) -> pathspec.PathSpec:
    patterns = list(_DEFAULT_IGNORES)
    gitignore = repo_root / ".gitignore"
    if gitignore.exists():
        patterns.extend(gitignore.read_text().splitlines())
    return pathspec.PathSpec.from_lines("gitignore", patterns)


def iter_source_files(
    repo_path: str | Path,
    include_languages: set[str] | None = None,
) -> Iterator[Path]:
    root = Path(repo_path).resolve()
    spec = _load_gitignore(root)

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if spec.match_file(str(rel)):
            continue
        lang = detect_language(path)
        if lang is None:
            continue
        if include_languages and lang not in include_languages:
            continue
        yield path
