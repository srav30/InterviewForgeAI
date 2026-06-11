import asyncio

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.orchestrator import run_orchestrator

router = APIRouter(prefix="/api/interview", tags=["interview"])


class StartInterviewRequest(BaseModel):
    job_description: str = Field(min_length=1)
    resume: str = Field(min_length=1)


class StartInterviewResponse(BaseModel):
    question: str
    tools_used: list[str] = Field(default_factory=list)


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(payload: StartInterviewRequest) -> StartInterviewResponse:
    result = await asyncio.to_thread(
        run_orchestrator,
        payload.job_description,
        payload.resume,
    )
    return StartInterviewResponse(
        question=result.question,
        tools_used=result.tools_used,
    )
