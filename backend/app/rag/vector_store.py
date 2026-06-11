"""Chroma-backed vector store for interview questions and rubrics."""

from pathlib import Path
from typing import Any

import chromadb
from openai import OpenAI

from app.config import get_settings
from app.rag.models import Chunk, RetrievalResult

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


class ChromaVectorStore:
    """Persist chunks and OpenAI embeddings in a local Chroma collection."""

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str | None = None,
        embedding_model: str | None = None,
    ) -> None:
        settings = get_settings()
        self.embedding_model = embedding_model or settings.embedding_model
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.chroma_client = chromadb.PersistentClient(
            path=str(persist_directory or settings.chroma_path)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name or settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def count(self) -> int:
        return self.collection.count()

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        embeddings = self._embed([chunk.text for chunk in chunks])
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[_metadata_for_chunk(chunk) for chunk in chunks],
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        where: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_embedding = self._embed([query])[0]
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "distances", "metadatas"],
        )
        return _retrieval_results_from_chroma(result)

    def get_by_metadata(
        self,
        where: dict[str, str],
        limit: int = 5,
    ) -> list[Chunk]:
        result = self.collection.get(
            where=where,
            limit=limit,
            include=["documents", "metadatas"],
        )
        ids = result.get("ids") or []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        chunks: list[Chunk] = []
        for chunk_id, text, metadata in zip(ids, documents, metadatas, strict=True):
            metadata = {key: str(value) for key, value in dict(metadata or {}).items()}
            chunks.append(
                Chunk(
                    id=str(metadata.pop("chunk_id", chunk_id)),
                    document_id=str(metadata.pop("document_id", chunk_id)),
                    text=text or "",
                    metadata=metadata,
                )
            )
        return chunks

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]


def _metadata_for_chunk(chunk: Chunk) -> dict[str, str]:
    return {
        **chunk.metadata,
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
    }


def _retrieval_results_from_chroma(result: dict[str, Any]) -> list[RetrievalResult]:
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    retrieval_results: list[RetrievalResult] = []
    for chunk_id, text, distance, metadata in zip(
        ids,
        documents,
        distances,
        metadatas,
        strict=True,
    ):
        metadata = dict(metadata or {})
        retrieval_results.append(
            RetrievalResult(
                chunk=Chunk(
                    id=str(metadata.pop("chunk_id", chunk_id)),
                    document_id=str(metadata.pop("document_id", "")),
                    text=text or "",
                    metadata={key: str(value) for key, value in metadata.items()},
                ),
                score=1 - float(distance),
            )
        )

    return retrieval_results
