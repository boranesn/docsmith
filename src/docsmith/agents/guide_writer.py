"""Guide writer agent: generate README, getting-started, API reference, and config docs."""

import anthropic

from docsmith.agents.state import DocsmithState
from docsmith.config import settings
from docsmith.models import DocPage, ParsedClass, ParsedFunction


def guide_writer_agent(state: DocsmithState) -> dict:
    functions = state.get("parsed_functions", [])
    classes = state.get("parsed_classes", [])
    arch = state.get("architecture_summary", "")
    repo = state["repo_path"]
    lang_breakdown = state.get("language_breakdown", {})
    entry_points = state.get("entry_points", [])

    api_pages = _generate_api_reference(functions, classes, repo)
    guide_pages = _generate_guides(arch, functions, classes, repo, lang_breakdown, entry_points)

    return {
        "api_pages": api_pages,
        "guide_pages": guide_pages,
        "agent_trace": state.get("agent_trace", []) + ["guide_writer"],
    }


def _generate_api_reference(
    functions: list[ParsedFunction],
    classes: list[ParsedClass],
    repo: str,
) -> list[DocPage]:
    pages: list[DocPage] = []
    public_fns = [f for f in functions if f.is_public]
    public_cls = [c for c in classes if c.is_public]

    if not public_fns and not public_cls:
        return pages

    # Group by file
    from collections import defaultdict
    by_file: dict[str, list] = defaultdict(list)
    for fn in public_fns:
        by_file[fn.file_path].append(("fn", fn))
    for cls in public_cls:
        by_file[cls.file_path].append(("cls", cls))

    index_lines = ["# API Reference\n"]
    for fpath, items in list(by_file.items())[:10]:
        short = fpath.replace(repo, "").lstrip("/")
        index_lines.append(f"## `{short}`\n")
        for kind, item in items:
            if kind == "fn":
                doc = item.docstring or "_No docstring._"
                index_lines.append(f"### `{item.signature}`\n\n{doc}\n")
            else:
                doc = item.docstring or "_No docstring._"
                index_lines.append(f"### class `{item.name}`\n\n{doc}\n")

    pages.append(DocPage(
        title="API Reference",
        filename="api-reference/index.md",
        content="\n".join(index_lines),
        category="api",
        source_files=list(by_file.keys()),
    ))
    return pages


def _generate_guides(
    arch: str,
    functions: list[ParsedFunction],
    classes: list[ParsedClass],
    repo: str,
    lang_breakdown: dict[str, int],
    entry_points: list[str],
) -> list[DocPage]:
    pages: list[DocPage] = []

    readme = _call_claude(_readme_prompt(arch, lang_breakdown, entry_points, repo))
    pages.append(DocPage(
        title="README",
        filename="README.md",
        content=readme,
        category="guide",
    ))

    getting_started = _call_claude(_getting_started_prompt(arch, entry_points, lang_breakdown))
    pages.append(DocPage(
        title="Getting Started",
        filename="guides/getting-started.md",
        content=getting_started,
        category="guide",
    ))

    arch_doc = f"# Architecture\n\n{arch}\n"
    pages.append(DocPage(
        title="Architecture",
        filename="ARCHITECTURE.md",
        content=arch_doc,
        category="architecture",
    ))

    return pages


def _readme_prompt(arch: str, lang_breakdown: dict, entry_points: list[str], repo: str) -> str:
    return f"""Generate a professional README.md for this project.

Repository: {repo}
Architecture summary:
{arch[:2000]}

Languages: {lang_breakdown}
Entry points: {entry_points[:5]}

The README must include:
- Project name and one-liner description
- Key features (bullet list)
- Quick start / installation instructions
- Basic usage example
- Tech stack table

Use Markdown formatting. Make it compelling and clear."""


def _getting_started_prompt(arch: str, entry_points: list[str], lang_breakdown: dict) -> str:
    return f"""Write a "Getting Started" guide for a developer new to this project.

Architecture:
{arch[:1500]}

Entry points: {entry_points[:5]}
Languages: {lang_breakdown}

Include:
1. Prerequisites
2. Installation steps
3. Configuration
4. Running the project for the first time
5. Running tests

Use numbered steps and code blocks where appropriate."""


def _call_claude(prompt: str) -> str:
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text  # type: ignore[index]
    except Exception as e:
        return f"_Documentation generation failed: {e}_"
