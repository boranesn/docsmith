"""Cyclomatic complexity computation for Python functions."""

import ast
from pathlib import Path

from docsmith.models import ParsedFunction

_BRANCH_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler,
    ast.With, ast.Assert, ast.comprehension,
)


def compute_complexity(fn: ParsedFunction, source_lines: list[str]) -> int:
    """Estimate McCabe cyclomatic complexity for a parsed function."""
    start = fn.line_start - 1
    end = fn.line_end
    snippet = "\n".join(source_lines[start:end])
    try:
        tree = ast.parse(snippet)
    except SyntaxError:
        return 1

    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, _BRANCH_NODES):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
    return complexity


def annotate_complexity(functions: list[ParsedFunction], source_lines: list[str]) -> list[ParsedFunction]:
    """Return functions with complexity_score populated."""
    for fn in functions:
        fn.complexity_score = compute_complexity(fn, source_lines)
    return functions
