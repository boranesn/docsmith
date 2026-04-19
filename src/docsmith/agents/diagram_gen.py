"""Diagram generator agent: produce Mermaid diagrams from module graph and data flow."""

from docsmith.agents.state import DocsmithState
from docsmith.analysis.dependency import to_mermaid
from docsmith.config import settings

import anthropic


def diagram_gen_agent(state: DocsmithState) -> dict:
    module_graph = state.get("module_graph", {})
    arch_summary = state.get("architecture_summary", "")

    diagrams: list[str] = []

    # Dependency graph from static analysis
    if module_graph:
        dep_diagram = to_mermaid(module_graph)
        diagrams.append(dep_diagram)

    # Data flow diagram via Claude
    if arch_summary:
        flow_diagram = _generate_flow_diagram(arch_summary)
        if flow_diagram:
            diagrams.append(flow_diagram)

    return {
        "diagrams": diagrams,
        "agent_trace": state.get("agent_trace", []) + ["diagram_gen"],
    }


def _generate_flow_diagram(arch_summary: str) -> str:
    prompt = f"""Based on this architecture summary, generate a Mermaid sequence diagram showing the main data flow.

Architecture:
{arch_summary[:1500]}

Return ONLY the Mermaid diagram code starting with "sequenceDiagram" or "flowchart TD". No explanation."""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()  # type: ignore[index]
        if text.startswith(("sequenceDiagram", "flowchart", "graph")):
            return text
        # Extract code block if wrapped
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith(("mermaid\n", "sequenceDiagram", "flowchart", "graph")):
                    return part.removeprefix("mermaid\n").strip()
        return text
    except Exception:
        return ""
