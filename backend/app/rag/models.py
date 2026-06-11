"""Shared RAG data models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float
