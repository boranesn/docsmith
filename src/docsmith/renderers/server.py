"""FastAPI local docs server."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse


def create_app(docs_dir: Path) -> FastAPI:
    app = FastAPI(title="docsmith docs", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        pages = sorted(docs_dir.rglob("*.md"))
        links = "\n".join(
            f'<li><a href="/doc/{p.relative_to(docs_dir)}">{p.relative_to(docs_dir)}</a></li>'
            for p in pages
        )
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>docsmith docs</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:40px auto;padding:0 20px}}</style>
</head><body>
<h1>📄 docsmith</h1>
<ul>{links}</ul>
</body></html>"""

    @app.get("/doc/{path:path}", response_class=HTMLResponse)
    async def serve_doc(path: str) -> str:
        file_path = docs_dir / path
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Document not found")

        content = file_path.read_text(encoding="utf-8")

        if file_path.suffix == ".md":
            try:
                import markdown
                html_body = markdown.markdown(content, extensions=["fenced_code", "tables"])
            except ImportError:
                html_body = f"<pre>{content}</pre>"

            return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{path}</title>
<style>body{{font-family:sans-serif;max-width:900px;margin:40px auto;padding:0 20px}}
pre{{background:#f4f4f4;padding:1em;border-radius:4px;overflow-x:auto}}</style>
</head><body>
<p><a href="/">← Back</a></p>
{html_body}
</body></html>"""

        return PlainTextResponse(content)  # type: ignore[return-value]

    @app.get("/diagrams/{name}", response_class=HTMLResponse)
    async def serve_diagram(name: str) -> str:
        mermaid_file = docs_dir / "diagrams" / name
        if not mermaid_file.exists():
            raise HTTPException(status_code=404)
        from docsmith.renderers.mermaid import wrap_html
        return wrap_html(mermaid_file.read_text(), title=name)

    return app
