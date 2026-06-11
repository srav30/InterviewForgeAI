from fastapi import APIRouter
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import get_settings

router = APIRouter(prefix="/api/interview", tags=["interview"])

SYSTEM_PROMPT = """\
You are a professional interviewer conducting a mock job interview.
You are given the job description and the candidate's resume.

Ask ONE strong opening interview question tailored to the role and the
candidate's background. Do not greet at length, do not explain yourself,
and do not ask more than one question. Return only the question text.
"""


class StartInterviewRequest(BaseModel):
    job_description: str = Field(min_length=1)
    resume: str = Field(min_length=1)


class StartInterviewResponse(BaseModel):
    question: str


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(payload: StartInterviewRequest) -> StartInterviewResponse:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    completion = await client.chat.completions.create(
        model=settings.interviewer_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"JOB DESCRIPTION:\n{payload.job_description}\n\n"
                    f"RESUME:\n{payload.resume}"
                ),
            },
        ],
        temperature=0.7,
    )

    question = (completion.choices[0].message.content or "").strip()
    return StartInterviewResponse(question=question)
