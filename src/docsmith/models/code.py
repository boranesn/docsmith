from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Parameter(BaseModel):
    name: str
    type_annotation: str | None = None
    default: str | None = None


class ParsedFunction(BaseModel):
    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    signature: str
    docstring: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    return_type: str | None = None
    is_public: bool = True
    complexity_score: int = 1
    calls: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)


class ParsedClass(BaseModel):
    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    docstring: str | None = None
    methods: list[ParsedFunction] = Field(default_factory=list)
    bases: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    is_public: bool = True


class APIEndpoint(BaseModel):
    path: str
    method: str
    function_name: str
    file_path: str
    description: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    response_model: str | None = None
    tags: list[str] = Field(default_factory=list)


class CodeChunk(BaseModel):
    id: str
    content: str
    file_path: str
    language: str
    chunk_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocPage(BaseModel):
    title: str
    filename: str
    content: str
    category: str  # "api", "guide", "architecture", "diagram"
    source_files: list[str] = Field(default_factory=list)


class DocCoverage(BaseModel):
    total_public_symbols: int
    documented_symbols: int
    coverage_pct: float
    undocumented: list[str] = Field(default_factory=list)
    by_file: dict[str, float] = Field(default_factory=dict)


class RunMetadata(BaseModel):
    run_id: str
    repo_path: str
    started_at: datetime
    finished_at: datetime | None = None
    coverage: DocCoverage | None = None
    language_breakdown: dict[str, int] = Field(default_factory=dict)
    agent_trace: list[str] = Field(default_factory=list)
    quality_score: float = 0.0
    output_path: str = ""
