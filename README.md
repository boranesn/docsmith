<div align="center">

# 📝 Docsmith

**An autonomous multi-agent system that reads any codebase and generates production-quality documentation with zero human input.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Agentic-LangGraph-orange.svg)](https://python.langchain.com/v0.1/docs/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Table of Contents
- [🎯 Why Docsmith?](#-why-docsmith)
- [✨ Key Features](#-key-features)
- [🚀 Getting Started](#-getting-started)
- [🛠️ Tech Stack](#️-tech-stack)
- [🤖 Multi-Agent Architecture](#-multi-agent-architecture)
- [🔍 Deep Dive: How It Works](#-deep-dive-how-it-works)
- [📁 Repository Structure](#-repository-structure)

---

## 🎯 Why Docsmith?

Documentation is always out of date because writing and maintaining it is a painful, manual process. `docsmith` solves this by pointing at any Git repository and producing a complete documentation suite. It runs a pipeline of specialized AI agents, each responsible for a distinct layer of codebase understanding, ensuring your docs are always accurate, comprehensive, and perfectly formatted.

## ✨ Key Features

- **Multi-Agent Orchestration:** Utilizes a directed graph of 6 specialized AI agents (Explorer, API Extractor, Architect, Guide Writer, Diagram Gen, Reviewer).
- **Language-Agnostic Parsing:** Uses `tree-sitter` to parse ASTs across 40+ languages without executing the code.
- **Semantic Code Search:** Leverages `chromadb` to create embeddings and retrieve context efficiently.
- **Auto-Generated Diagrams:** Produces programmatic architecture and dependency diagrams using Mermaid.
- **Incremental Updates (Watch Mode):** Monitors file changes and re-generates *only* the affected documentation pages in seconds.
- **Coverage Reporting:** Calculates exactly what percentage of your public API is documented.

---

## 🚀 Getting Started

### Installation

*Note: docsmith is packaged using `uv`.*

```bash
# Clone the repository
git clone https://github.com/boranesn/docsmith.git
cd docsmith

# Install dependencies
uv sync
```

### Usage Examples

```bash
# Generate docs for a local project
docsmith run ./my-project --output ./docs

# Generate docs directly from a GitHub URL
docsmith run https://github.com/fastapi/fastapi --output ./fastapi-docs

# Watch mode: Re-generate instantly on file changes
docsmith watch ./my-project

# Diff mode: Only document what changed in recent commits
docsmith diff ./my-project --since HEAD~5

# Serve generated docs via a local live-reloading dev server
docsmith serve ./docs --port 8080
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Core runtime environment. |
| **AST Parsing** | `tree-sitter` | Language-agnostic AST extraction for 40+ languages. |
| **Agent Orchestration** | `LangGraph` | Stateful multi-agent graph with cyclic workflows. |
| **LLM Engine** | Anthropic Claude API | Handles long contexts for large files and precise tool usage. |
| **Embeddings & Search** | `chromadb` | Semantic search over codebase semantic chunks. |
| **File Watching** | `watchfiles` | Rust-backed, high-performance async file system events. |
| **Diagrams** | `diagrams` + Mermaid | Programmatic architecture and flow visualizations. |
| **CLI Framework** | `Typer` + `Rich` | Beautiful, robust terminal interfaces. |
| **Validation** | `Pydantic v2` | Strict data structuring and typing. |
| **HTTP Server** | `FastAPI` | Serving generated docs via a local dev server. |

---

## 🤖 Multi-Agent Architecture

The `docsmith` pipeline isn't a simple linear chain; it is a **directed graph** with conditional routing and retry loops, ensuring high quality and consistency.

```text
                    ┌─────────────────────────────┐
                    │         START               │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Explorer Agent            │
                    │   • Read repo structure     │
                    │   • Detect lang/framework   │
                    │   • Identify entry points   │
                    └──────────────┬──────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
  ┌────────────▼──────┐  ┌─────────▼──────┐  ┌────────▼──────────┐
  │ API Extractor     │  │ Architect      │  │ Diagram Gen       │
  │ • Parse AST       │  │ • Map modules  │  │ • Component graph │
  │ • Find public APIs│  │ • Infer roles  │  │ • Data flow       │
  │ • Extract types   │  │ • Data flows   │  │ • Mermaid output  │
  └────────────┬──────┘  └─────────┬──────┘  └────────┬──────────┘
               │                   │                   │
               └───────────────────┼───────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Guide Writer Agent        │
                    │   • README.md               │
                    │   • Getting Started guide   │
                    │   • API references          │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Reviewer Agent            │
                    │   • Consistency check       │
                    │   • Accuracy validation     │
                    │   • Coverage score          │
                    │   [if quality < threshold]  │
                    │   → route back to writer    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │         END                 │
                    │   Write files to disk       │
                    └─────────────────────────────┘
```

---

## 🔍 Deep Dive: How It Works

### AST Parsing

`tree-sitter` extracts structural context from source files without executing them.

- **Python:** Extracts functions, methods, classes, Pydantic models, and FastAPI route decorators.
- **TypeScript:** Extracts interfaces, types, exported functions, and React component props.

### Dependency Graphs

The system builds a directed graph of module imports and renders it directly as Mermaid syntax. Nodes are intelligently sized based on fan-in (number of dependents), visually highlighting the most critical modules in your codebase.

### Documentation Coverage

`docsmith` doesn't just write docs; it tells you what's missing. After every run, you receive a detailed CLI report:

```text
Documentation Coverage: 74.3%  ████████████████░░░░░░

  Fully documented:   43 symbols
  Missing docs:       15 symbols

  Lowest coverage:
    src/auth/jwt.py        — 20%  (4 of 5 functions undocumented)
    src/db/migrations.py   — 33%  (2 of 3 undocumented)
```

---

## 📁 Repository Structure

```text
docsmith/
├── src/
│   └── docsmith/
│       ├── cli/                # Typer commands (run, watch, diff, serve)
│       ├── ingestion/          # File walking, Tree-sitter parsing, ChromaDB embeddings
│       ├── agents/             # LangGraph state definitions and 6 distinct agents
│       ├── analysis/           # Dependency graphs, complexity scoring, coverage calculation
│       ├── renderers/          # Markdown formatting, Mermaid generation, FastAPI server
│       ├── storage/            # ChromaDB management and run state persistence
│       ├── models/             # Pydantic v2 schemas (CodeChunk, ParsedFunction, etc.)
│       └── config.py           # Pydantic BaseSettings for the app
├── pyproject.toml
└── README.md
```

---

## License

MIT

---


<div align="center">
  <i>Built with logic, agents, and coffee. ☕</i>
</div>
