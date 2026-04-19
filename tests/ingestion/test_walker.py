from pathlib import Path

import pytest

from docsmith.ingestion.walker import iter_source_files


def test_walker_finds_python_files(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def foo(): pass")
    (tmp_path / "README.md").write_text("# readme")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython-312.pyc").write_bytes(b"")

    files = list(iter_source_files(tmp_path))
    names = {f.name for f in files}

    assert "main.py" in names
    assert "utils.py" in names
    assert "main.cpython-312.pyc" not in names


def test_walker_respects_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("secret.py\n")
    (tmp_path / "secret.py").write_text("SECRET = 'password'")
    (tmp_path / "public.py").write_text("def hi(): pass")

    files = list(iter_source_files(tmp_path))
    names = {f.name for f in files}

    assert "public.py" in names
    assert "secret.py" not in names


def test_walker_language_filter(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("pass")
    (tmp_path / "index.ts").write_text("export const x = 1;")

    py_only = list(iter_source_files(tmp_path, include_languages={"python"}))
    assert all(f.suffix == ".py" for f in py_only)
