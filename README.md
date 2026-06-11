# InterviewForge AI

AI-powered mock interview platform. Paste a job description + resume, run a
multi-turn interview with real-time evaluation, and get a scored report with
improvement recommendations.

## Repo layout

```
backend/    FastAPI + OpenAI (Python 3.12, managed with uv)
frontend/   Next.js + Tailwind CSS
```

## Backend — local dev

```powershell
cd backend
copy .env.example .env   # then put your real OPENAI_API_KEY in .env
uv run uvicorn app.main:app --reload --port 8000
```

- Health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/docs

## Frontend — local dev

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Current state

`POST /api/interview/start` runs a **Strands orchestrator** with two sub-agents:

- **question_retriever** — searches a ChromaDB question bank (18 seed questions)
- **rubric_specialist** — retrieves scoring rubrics linked to those questions

The orchestrator uses retrieved bank content to ask one tailored opening question.
Response includes optional `tools_used` for debugging.

Still to come: multi-turn replies, scored report, Supabase sessions, LangSmith, Ragas.

### ChromaDB (local)

Seed data lives in `backend/data/question_bank.json`. On startup, the API ingests
into `backend/data/chroma/` if the collection is empty.

Force re-ingest locally:

```powershell
cd backend
uv run python -c "from app.rag.ingest import ingest_question_bank; print(ingest_question_bank(force=True))"
```

### Railway volume

Mount a volume at **`/app/data/chroma`** (root directory is `backend/`). Set:

```
CHROMA_PATH=data/chroma
INGEST_ON_STARTUP=true
```

First deploy ingests the seed bank; later deploys reuse persisted Chroma data.
