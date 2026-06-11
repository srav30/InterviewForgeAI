"""Strands tools for question bank and rubric retrieval."""

from typing import Any

from strands import tool

from app.rag.vector_store import ChromaVectorStore


def _serialize_results(results: list) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": result.chunk.id,
            "question_id": result.chunk.metadata.get("question_id", result.chunk.id),
            "text": result.chunk.text,
            "score": round(result.score, 4),
            "metadata": result.chunk.metadata,
        }
        for result in results
    ]


@tool
def search_question_bank(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search the curated interview question bank for questions relevant to a query.

    Pass a combined job-description and resume summary as the query. Returns
    question text plus metadata such as category, topic, difficulty, and question_id.
    """
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    results = ChromaVectorStore().search(
        normalized_query,
        top_k=top_k,
        where={"type": "question"},
    )
    return _serialize_results(results)


@tool
def search_rubrics(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Search scoring rubrics by topic, category, or evaluation criteria."""
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    results = ChromaVectorStore().search(
        normalized_query,
        top_k=top_k,
        where={"type": "rubric"},
    )
    return [
        {
            "chunk_id": result.chunk.id,
            "question_id": result.chunk.metadata.get("question_id", ""),
            "rubric_text": result.chunk.text,
            "score": round(result.score, 4),
            "metadata": result.chunk.metadata,
        }
        for result in results
    ]


@tool
def get_rubric_for_question(question_id: str) -> dict[str, Any]:
    """Fetch the rubric linked to a specific question_id from the question bank."""
    normalized_id = question_id.strip()
    if not normalized_id:
        raise ValueError("question_id must not be empty")

    chunks = ChromaVectorStore().get_by_metadata(
        where={"type": "rubric", "question_id": normalized_id},
        limit=1,
    )
    if not chunks:
        return {"question_id": normalized_id, "found": False, "rubric_text": ""}

    chunk = chunks[0]
    return {
        "question_id": normalized_id,
        "found": True,
        "rubric_text": chunk.text,
        "metadata": chunk.metadata,
    }
