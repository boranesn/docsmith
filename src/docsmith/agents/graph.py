"""LangGraph StateGraph: wires all 6 agents with conditional retry routing."""

from pathlib import Path

from langgraph.graph import END, START, StateGraph

from docsmith.agents.api_extractor import api_extractor_agent
from docsmith.agents.architect import architect_agent
from docsmith.agents.diagram_gen import diagram_gen_agent
from docsmith.agents.explorer import explorer_agent
from docsmith.agents.guide_writer import guide_writer_agent
from docsmith.agents.reviewer import reviewer_agent, should_retry
from docsmith.agents.state import DocsmithState
from docsmith.renderers.markdown import render_docs


def build_graph() -> StateGraph:
    graph = StateGraph(DocsmithState)

    graph.add_node("explorer", explorer_agent)
    graph.add_node("api_extractor", api_extractor_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("diagram_gen", diagram_gen_agent)
    graph.add_node("guide_writer", guide_writer_agent)
    graph.add_node("reviewer", reviewer_agent)

    graph.add_edge(START, "explorer")

    # Parallel after explorer
    graph.add_edge("explorer", "api_extractor")
    graph.add_edge("explorer", "architect")
    graph.add_edge("explorer", "diagram_gen")

    # Merge into guide_writer
    graph.add_edge("api_extractor", "guide_writer")
    graph.add_edge("architect", "guide_writer")
    graph.add_edge("diagram_gen", "guide_writer")

    graph.add_edge("guide_writer", "reviewer")

    # Conditional retry loop
    graph.add_conditional_edges(
        "reviewer",
        should_retry,
        {"retry": "guide_writer", "end": END},
    )

    return graph


async def run_pipeline(
    repo_path: str,
    output_path: Path,
    changed_files: set[str] | None = None,
    reset: bool = False,
) -> dict:
    output_path = Path(output_path)

    initial_state: DocsmithState = {
        "repo_path": repo_path,
        "output_path": str(output_path),
        "changed_files": changed_files or set(),
        "language_breakdown": {},
        "entry_points": [],
        "parsed_functions": [],
        "parsed_classes": [],
        "module_graph": {},
        "architecture_summary": "",
        "api_pages": [],
        "guide_pages": [],
        "diagrams": [],
        "review_notes": [],
        "quality_score": 0.0,
        "retry_count": 0,
        "agent_trace": [],
        "coverage": None,
        "messages": [],
    }

    compiled = build_graph().compile()
    final_state = await compiled.ainvoke(initial_state)

    render_docs(final_state, output_path)

    return {
        "quality_score": final_state.get("quality_score", 0.0),
        "language_breakdown": final_state.get("language_breakdown", {}),
        "agent_trace": final_state.get("agent_trace", []),
        "coverage": final_state.get("coverage"),
    }
