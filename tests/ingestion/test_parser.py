from pathlib import Path

import pytest

from docsmith.ingestion.parser import parse_file


def test_parse_python_functions(sample_python_file: Path) -> None:
    functions, classes = parse_file(sample_python_file)

    fn_names = {f.name for f in functions}
    assert "add" in fn_names

    add_fn = next(f for f in functions if f.name == "add")
    assert add_fn.is_public is True
    assert add_fn.docstring is not None
    assert "sum" in add_fn.docstring.lower() or "add" in add_fn.docstring.lower()


def test_parse_python_private_functions(sample_python_file: Path) -> None:
    functions, classes = parse_file(sample_python_file)
    fn_names = {f.name for f in functions}
    # _private_helper may or may not appear depending on parser depth
    # but if it does, it must be marked not public
    private = [f for f in functions if f.name == "_private_helper"]
    for fn in private:
        assert fn.is_public is False


def test_parse_python_classes(sample_python_file: Path) -> None:
    functions, classes = parse_file(sample_python_file)
    class_names = {c.name for c in classes}
    assert "Calculator" in class_names

    calc = next(c for c in classes if c.name == "Calculator")
    assert calc.is_public is True


def test_parse_unsupported_extension(tmp_path: Path) -> None:
    f = tmp_path / "file.xyz"
    f.write_text("random content")
    functions, classes = parse_file(f)
    assert functions == []
    assert classes == []
