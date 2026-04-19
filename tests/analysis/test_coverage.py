import pytest

from docsmith.analysis.coverage import compute_coverage
from docsmith.models import ParsedClass, ParsedFunction, Parameter


def _make_fn(name: str, docstring: str | None = None, is_public: bool = True) -> ParsedFunction:
    return ParsedFunction(
        name=name,
        file_path="test.py",
        line_start=1,
        line_end=5,
        language="python",
        signature=f"def {name}()",
        docstring=docstring,
        is_public=is_public,
    )


def test_full_coverage() -> None:
    fns = [_make_fn("foo", "Does foo."), _make_fn("bar", "Does bar.")]
    coverage = compute_coverage(fns, [])
    assert coverage.total_public_symbols == 2
    assert coverage.documented_symbols == 2
    assert coverage.coverage_pct == 100.0


def test_partial_coverage() -> None:
    fns = [_make_fn("foo", "Has doc"), _make_fn("bar", None)]
    coverage = compute_coverage(fns, [])
    assert coverage.coverage_pct == 50.0
    assert "bar" in coverage.undocumented


def test_private_excluded() -> None:
    fns = [_make_fn("_private", "Has doc", is_public=False), _make_fn("public", None)]
    coverage = compute_coverage(fns, [])
    assert coverage.total_public_symbols == 1


def test_zero_symbols() -> None:
    coverage = compute_coverage([], [])
    assert coverage.coverage_pct == 0.0
    assert coverage.total_public_symbols == 0
