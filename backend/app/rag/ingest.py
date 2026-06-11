"""Ingest bundled question bank and rubrics into ChromaDB."""

import json
from pathlib import Path

from app.config import get_settings
from app.rag.models import Chunk
from app.rag.vector_store import ChromaVectorStore

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED_PATH = BACKEND_ROOT / "data" / "question_bank.json"


def _format_rubric_text(question_id: str, rubric: dict) -> str:
    lines = [f"Rubric for question {question_id}:"]
    dimensions = rubric.get("dimensions", {})
    for name, description in dimensions.items():
        lines.append(f"- {name}: {description}")

    scoring_bands = rubric.get("scoring_bands", {})
    if scoring_bands:
        lines.append("Scoring bands:")
        for score, description in sorted(scoring_bands.items()):
            lines.append(f"  {score}: {description}")

    return "\n".join(lines)


def _chunks_from_record(record: dict) -> list[Chunk]:
    question_id = record["id"]
    role_tags = record.get("role_tags", [])
    if isinstance(role_tags, list):
        role_tags = ",".join(role_tags)

    question_chunk = Chunk(
        id=question_id,
        document_id=question_id,
        text=record["question"],
        metadata={
            "type": "question",
            "category": record.get("category", "general"),
            "topic": record.get("topic", "general"),
            "difficulty": record.get("difficulty", "medium"),
            "role_tags": role_tags,
            "question_id": question_id,
        },
    )

    rubric_chunk = Chunk(
        id=f"{question_id}#rubric",
        document_id=question_id,
        text=_format_rubric_text(question_id, record.get("rubric", {})),
        metadata={
            "type": "rubric",
            "category": record.get("category", "general"),
            "topic": record.get("topic", "general"),
            "difficulty": record.get("difficulty", "medium"),
            "role_tags": role_tags,
            "question_id": question_id,
        },
    )
    return [question_chunk, rubric_chunk]


def load_seed_records(seed_path: Path | None = None) -> list[dict]:
    path = seed_path or DEFAULT_SEED_PATH
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("question bank seed file must contain a JSON list")
    return payload


def ingest_question_bank(
    seed_path: Path | None = None,
    *,
    force: bool = False,
) -> int:
    """Load seed questions/rubrics into Chroma. Returns number of chunks upserted."""
    store = ChromaVectorStore()
    if store.count > 0 and not force:
        return 0

    records = load_seed_records(seed_path)
    chunks: list[Chunk] = []
    for record in records:
        chunks.extend(_chunks_from_record(record))

    store.add(chunks)
    return len(chunks)


def ingest_if_empty() -> int:
    settings = get_settings()
    if not settings.ingest_on_startup:
        return 0
    return ingest_question_bank(force=False)
