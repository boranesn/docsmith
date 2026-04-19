from pathlib import Path

import chromadb
from chromadb import Collection

from docsmith.config import settings
from docsmith.models import CodeChunk


class ChromaStore:
    COLLECTION_NAME = "docsmith_code"

    def __init__(self, chroma_path: Path | None = None) -> None:
        path = chroma_path or settings.chroma_dir
        path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(path))
        self._collection: Collection = self._client.get_or_create_collection(
            self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[CodeChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.add(
            ids=[c.id for c in chunks],
            documents=[c.content for c in chunks],
            embeddings=embeddings,
            metadatas=[{"file_path": c.file_path, "language": c.language} for c in chunks],
        )

    def query(self, embedding: list[float], n_results: int = 10) -> list[str]:
        results = self._collection.query(query_embeddings=[embedding], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return docs  # type: ignore[return-value]

    def reset(self) -> None:
        self._client.delete_collection(self.COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(self.COLLECTION_NAME)

    def count(self) -> int:
        return self._collection.count()
