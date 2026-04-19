from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from docsmith.models import DocCoverage, DocPage, ParsedClass, ParsedFunction


class DocsmithState(TypedDict):
    repo_path: str
    output_path: str
    changed_files: set[str]
    language_breakdown: dict[str, int]
    entry_points: list[str]
    parsed_functions: list[ParsedFunction]
    parsed_classes: list[ParsedClass]
    module_graph: dict[str, list[str]]
    architecture_summary: str
    api_pages: list[DocPage]
    guide_pages: list[DocPage]
    diagrams: list[str]
    review_notes: list[str]
    quality_score: float
    retry_count: int
    agent_trace: list[str]
    coverage: DocCoverage | None
    messages: Annotated[list, add_messages]
