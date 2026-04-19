import hashlib
from pathlib import Path

from docsmith.config import settings
from docsmith.models import CodeChunk, ParsedFunction


def chunk_functions(
    functions: list[ParsedFunction],
    source_lines: list[str],
    file_path: str,
    language: str,
) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []
    for i, fn in enumerate(functions):
        start = max(0, fn.line_start - 1)
        end = min(len(source_lines), fn.line_end)
        content = "\n".join(source_lines[start:end])
        chunk_id = hashlib.sha256(f"{file_path}:{fn.name}:{i}".encode()).hexdigest()[:16]
        chunks.append(CodeChunk(
            id=chunk_id,
            content=content,
            file_path=file_path,
            language=language,
            chunk_index=i,
            metadata={"function_name": fn.name, "is_public": fn.is_public},
        ))
    return chunks


def chunk_file(path: Path, chunk_size: int | None = None, overlap: int | None = None) -> list[CodeChunk]:
    """Sliding-window chunker for files without structured parsing."""
    size = chunk_size or settings.chunk_size
    ov = overlap or settings.chunk_overlap
    source = path.read_text(errors="replace")
    lines = source.splitlines()
    chunks: list[CodeChunk] = []
    step = max(1, size - ov)
    i = 0
    idx = 0
    while i < len(lines):
        block = "\n".join(lines[i : i + size])
        chunk_id = hashlib.sha256(f"{path}:{i}".encode()).hexdigest()[:16]
        chunks.append(CodeChunk(
            id=chunk_id,
            content=block,
            file_path=str(path),
            language="unknown",
            chunk_index=idx,
        ))
        i += step
        idx += 1
    return chunks
