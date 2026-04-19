# docsmith

> An autonomous multi-agent system that reads any codebase and generates production-quality documentation — API references, architecture diagrams, README files, and onboarding guides — with zero human input.

---

## 🎯 What It Does

Documentation is always out of date because writing it is painful. `docsmith` points at any Git repository and produces a complete documentation suite by running a pipeline of specialized AI agents, each responsible for a distinct layer of understanding.

```bash
# Example usage
docsmith run ./my-project --output ./docs
docsmith run https://github.com/fastapi/fastapi --output ./fastapi-docs
docsmith watch ./my-project              # Re-generate on file changes
docsmith diff ./my-project --since HEAD~5  # Only document what changed
docsmith serve ./docs --port 8080        # Serve docs locally
```

**Output for any repo:**
```
docs/
├── README.md               # Auto-generated project overview
├── ARCHITECTURE.md         # System design & component relationships
├── api-reference/
│   ├── index.md            # All public functions/classes
│   ├── authentication.md
│   └── data-models.md
├── guides/
│   ├── getting-started.md
│   ├── configuration.md
│   └── deployment.md
├── diagrams/
│   ├── architecture.mermaid
│   ├── data-flow.mermaid
│   └── module-dependencies.mermaid
└── docsmith.json           # Metadata: coverage %, last run, agent trace
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.12+ | |
| AST parsing | `tree-sitter` + `tree-sitter-languages` | Language-agnostic AST for 40+ languages |
| Agent orchestration | `LangGraph` | Stateful multi-agent graph with cycles |
| LLM | Anthropic Claude API | Long context for large files, tool use |
| Embeddings + search | `chromadb` | Semantic search over codebase chunks |
| File watching | `watchfiles` | Rust-backed, async file system events |
| Diagram generation | `diagrams` (Graphviz) + Mermaid | Programmatic architecture diagrams |
| CLI | `Typer` + `Rich` | |
| Validation | `Pydantic v2` | |
| HTTP server | `FastAPI` | Serve generated docs via local dev server |
| Packaging | `uv` | |
| Testing | `pytest-asyncio` | |
| Linting | `Ruff` + `mypy` | |

---

## 📁 Repository Structure

```
docsmith/
├── src/
│   └── docsmith/
│       ├── __init__.py
│       ├── cli/
│       │   ├── app.py          # Typer root
│       │   ├── run.py          # `docsmith run` — main command
│       │   ├── watch.py        # `docsmith watch`
│       │   ├── diff.py         # `docsmith diff`
│       │   └── serve.py        # `docsmith serve`
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── walker.py       # Recursively walk repo, respect .gitignore
│       │   ├── parser.py       # tree-sitter AST extraction per language
│       │   ├── chunker.py      # Split code into semantic chunks for embedding
│       │   ├── embedder.py     # Embed chunks → ChromaDB
│       │   └── languages.py    # Language detection + tree-sitter grammar map
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── graph.py        # LangGraph StateGraph definition
│       │   ├── state.py        # Typed agent state (TypedDict)
│       │   ├── explorer.py     # Agent 1: understand repo structure & purpose
│       │   ├── api_extractor.py # Agent 2: extract all public APIs from AST
│       │   ├── architect.py    # Agent 3: infer architecture & component roles
│       │   ├── guide_writer.py # Agent 4: write getting-started & usage guides
│       │   ├── diagram_gen.py  # Agent 5: produce Mermaid diagrams
│       │   └── reviewer.py     # Agent 6: quality-check & consistency pass
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── dependency.py   # Build module import graph
│       │   ├── complexity.py   # Cyclomatic complexity per function
│       │   ├── coverage.py     # Doc coverage: what % of public API is documented
│       │   └── diff.py         # Git diff → changed symbols
│       ├── renderers/
│       │   ├── __init__.py
│       │   ├── markdown.py     # Render agent output → Markdown files
│       │   ├── mermaid.py      # Render dependency graph → Mermaid syntax
│       │   └── server.py       # FastAPI app for local docs serving
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── chroma.py       # ChromaDB collection management
│       │   └── state.py        # Persist docsmith run metadata (JSON)
│       ├── models/
│       │   └── __init__.py
│       │   └── code.py         # Pydantic v2: CodeChunk, ParsedFunction, APIEndpoint, DocPage
│       └── config.py           # Pydantic BaseSettings
├── tests/
│   ├── conftest.py
│   ├── ingestion/
│   │   ├── test_walker.py
│   │   ├── test_parser.py
│   │   └── fixtures/           # Sample Python/TS/Go files
│   ├── agents/
│   │   └── test_graph.py
│   └── analysis/
│       ├── test_dependency.py
│       └── test_coverage.py
├── pyproject.toml
├── .env.example
├── ruff.toml
├── mypy.ini
└── README.md
```

---

## 🤖 Multi-Agent Architecture (`src/docsmith/agents/graph.py`)

The agent pipeline is a **directed graph** with conditional routing — not a simple linear chain.

```
                    ┌─────────────────────────────┐
                    │         START               │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   explorer_agent            │
                    │   • Read repo structure     │
                    │   • Detect lang/framework   │
                    │   • Identify entry points   │
                    └──────────────┬──────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
  ┌────────────▼──────┐  ┌─────────▼──────┐  ┌────────▼──────────┐
  │  api_extractor    │  │  architect     │  │  diagram_gen      │
  │  • Parse AST      │  │  • Map modules │  │  • Dependency     │
  │  • Find all       │  │  • Infer roles │  │    graph          │
  │    public APIs    │  │  • Data flows  │  │  • Data flow      │
  │  • Extract types  │  │                │  │  • Mermaid output │
  └────────────┬──────┘  └─────────┬──────┘  └────────┬──────────┘
               │                   │                   │
               └───────────────────┼───────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   guide_writer_agent        │
                    │   • README.md               │
                    │   • Getting Started guide   │
                    │   • API reference pages     │
                    │   • Configuration guide     │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   reviewer_agent            │
                    │   • Consistency check       │
                    │   • Accuracy validation     │
                    │   • Coverage score          │
                    │                             │
                    │   [if quality < threshold]  │
                    │   → route back to writer    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │         END                 │
                    │   Write files to disk       │
                    └─────────────────────────────┘
```

### Agent State (`src/docsmith/agents/state.py`)

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class DocsmithState(TypedDict):
    repo_path: str
    language_breakdown: dict[str, int]       # {"python": 82, "yaml": 12, ...}
    entry_points: list[str]                  # Main modules/files
    parsed_functions: list[ParsedFunction]   # All public functions from AST
    module_graph: dict[str, list[str]]       # import dependency graph
    architecture_summary: str
    api_pages: list[DocPage]
    guide_pages: list[DocPage]
    diagrams: list[str]                      # Mermaid diagram strings
    review_notes: list[str]
    quality_score: float                     # 0.0 – 1.0
    retry_count: int
    messages: Annotated[list, add_messages]
```

---

## 🌳 AST Parsing (`src/docsmith/ingestion/parser.py`)

`tree-sitter` parses source files without executing them — works for Python, TypeScript, Go, Rust, Java, and 35+ more languages.

For each source file, the parser extracts:

```python
class ParsedFunction(BaseModel):
    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    signature: str              # e.g. "def fetch_user(user_id: int) -> User"
    docstring: str | None       # Existing docstring if present
    parameters: list[Parameter]
    return_type: str | None
    is_public: bool
    complexity_score: int       # Cyclomatic complexity
    calls: list[str]            # Functions this one calls
    decorators: list[str]       # e.g. ["@router.get", "@cached"]
```

**Python-specific extraction:**
- Functions, methods, classes, properties, class variables
- Pydantic model fields
- FastAPI route decorators → endpoint documentation

**TypeScript-specific extraction:**
- Interfaces, types, enums
- React component props
- Exported functions and classes

---

## 🗺️ Dependency Graph (`src/docsmith/analysis/dependency.py`)

Builds a directed graph of module imports — rendered as a Mermaid diagram.

```python
# Input: repo source files
# Output: Mermaid diagram string

"""
graph TD
    api/routes --> services/user
    api/routes --> services/auth
    services/user --> db/models
    services/auth --> db/models
    services/auth --> lib/jwt
    db/models --> config
"""
```

Nodes are sized by number of dependents (fan-in) — visually reveals the most critical modules.

---

## 📈 Documentation Coverage (`src/docsmith/analysis/coverage.py`)

```python
class DocCoverage(BaseModel):
    total_public_symbols: int
    documented_symbols: int
    coverage_pct: float
    undocumented: list[str]    # symbol names
    by_file: dict[str, float]  # file → coverage %
```

Reported in the CLI after each run:

```
Documentation Coverage: 74.3%  ████████████████░░░░░░

  Fully documented:   43 symbols
  Missing docs:       15 symbols

  Lowest coverage:
    src/auth/jwt.py        — 20%  (4 of 5 functions undocumented)
    src/db/migrations.py   — 33%  (2 of 3 undocumented)
```

---

## 🔄 Watch Mode (`docsmith watch`)

Uses `watchfiles` (Rust-backed) to monitor file system changes. On change:
1. Detect which symbols changed (git diff or file hash comparison)
2. Re-run only the affected agents (not the full pipeline)
3. Update only the changed doc pages

This makes incremental regeneration fast — typically under 5 seconds for a single changed file.

---

## 📦 Phases

### Phase 1 — Foundation (Day 1)
- [ ] `uv init docsmith`
- [ ] `pyproject.toml` — all deps
- [ ] `config.py` — Pydantic BaseSettings
- [ ] `models/code.py` — all Pydantic models
- [ ] `cli/app.py` — Typer skeleton
- [ ] `storage/state.py` — run metadata persistence
- [ ] `tests/conftest.py`
- [ ] Git: `feat: project foundation`

### Phase 2 — Ingestion Pipeline (Day 2)
- [ ] `ingestion/walker.py` — gitignore-aware file walker
- [ ] `ingestion/languages.py` — language detection by extension
- [ ] `ingestion/parser.py` — tree-sitter AST extraction (Python + TypeScript first)
- [ ] `ingestion/chunker.py` — semantic chunking
- [ ] `ingestion/embedder.py` — ChromaDB embedding + collection management
- [ ] `analysis/dependency.py` — import graph builder
- [ ] `analysis/complexity.py` — cyclomatic complexity scorer
- [ ] Tests with fixture Python/TS files
- [ ] Git: `feat: ingestion pipeline`

### Phase 3 — Agent Graph (Day 3–4)
- [ ] `agents/state.py` — TypedDict state definition
- [ ] `agents/graph.py` — LangGraph StateGraph with all 6 agents
- [ ] `agents/explorer.py`
- [ ] `agents/api_extractor.py`
- [ ] `agents/architect.py`
- [ ] `agents/diagram_gen.py`
- [ ] `agents/guide_writer.py`
- [ ] `agents/reviewer.py` + retry loop
- [ ] Git: `feat: multi-agent documentation pipeline`

### Phase 4 — Renderers & CLI (Day 5)
- [ ] `renderers/markdown.py`
- [ ] `renderers/mermaid.py`
- [ ] `analysis/coverage.py` — coverage reporter
- [ ] `cli/run.py` — full pipeline with Rich progress
- [ ] `cli/diff.py` — incremental re-generation
- [ ] `cli/watch.py` — watchfiles integration
- [ ] `renderers/server.py` + `cli/serve.py` — FastAPI local server
- [ ] Git: `feat: renderers and CLI commands`

### Phase 5 — Polish (Day 6)
- [ ] Integration test: run full pipeline on a small fixture repo
- [ ] Coverage ≥ 70%
- [ ] README with before/after doc examples
- [ ] Git: `docs: complete documentation`
- [ ] Tag: `v1.0.0`

---

## 🔑 What This Demonstrates

- **Multi-agent orchestration** — LangGraph state machine with conditional routing & retry loops
- **Language-agnostic AST parsing** — tree-sitter across 40+ languages
- **Semantic search over code** — ChromaDB embeddings for context retrieval
- **Long-context LLM usage** — Claude's 200K context for large file analysis
- **Real problem solved** — every engineering team needs this

---

*Built with Python 3.12 · LangGraph · tree-sitter · ChromaDB · Anthropic Claude · FastAPI · uv*
