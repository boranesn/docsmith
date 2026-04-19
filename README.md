# docsmith

> An autonomous multi-agent system that reads any codebase and generates production-quality documentation — API references, architecture diagrams, README files, and onboarding guides — with zero human input.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Generate docs for any repo
docsmith run ./my-project --output ./docs

# Watch for changes
docsmith watch ./my-project

# Serve docs locally
docsmith serve ./docs --port 8080
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| AST parsing | `tree-sitter` |
| Agent orchestration | `LangGraph` |
| LLM | Anthropic Claude |
| Embeddings | `chromadb` |
| File watching | `watchfiles` |
| CLI | `Typer` + `Rich` |
| HTTP server | `FastAPI` |

## Development

```bash
# Install dev deps
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
mypy src/
```

*Built with Python 3.12 · LangGraph · tree-sitter · ChromaDB · Anthropic Claude · FastAPI · uv*
