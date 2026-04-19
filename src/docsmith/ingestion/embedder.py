"""Lightweight embedder using sentence-transformers or a fallback hash-based stub."""

from __future__ import annotations

from docsmith.models import CodeChunk


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = None
        self._model_name = model_name
        self._dim = 384

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        except ImportError:
            self._model = None  # type: ignore[assignment]

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._load()
        if self._model is not None:
            return self._model.encode(texts, show_progress_bar=False).tolist()  # type: ignore[union-attr]
        return [self._hash_embed(t) for t in texts]

    def embed_chunks(self, chunks: list[CodeChunk]) -> list[list[float]]:
        return self.embed([c.content for c in chunks])

    def _hash_embed(self, text: str) -> list[float]:
        import hashlib
        digest = hashlib.sha256(text.encode()).digest()
        vec = [((b - 128) / 128.0) for b in digest]
        vec.extend([0.0] * (self._dim - len(vec)))
        return vec[: self._dim]
