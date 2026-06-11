"""Rubric retrieval sub-agent."""

from strands import Agent
from strands.models.openai import OpenAIModel

from app.config import get_settings
from app.tools.question_bank import get_rubric_for_question, search_rubrics

RUBRIC_SPECIALIST_PROMPT = """
You are a rubric specialist for mock interview evaluation.

Use get_rubric_for_question when you know a question_id.
Use search_rubrics when you need rubrics by topic, category, or evaluation theme.

Summarize the scoring dimensions and what strong vs weak answers look like.
Do not invent rubric criteria that were not retrieved from the tools.
""".strip()


def build_rubric_specialist_agent() -> Agent:
    settings = get_settings()
    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.interviewer_model,
        params={"max_tokens": 800, "temperature": 0.2},
    )
    return Agent(
        name="rubric_specialist",
        system_prompt=RUBRIC_SPECIALIST_PROMPT,
        tools=[get_rubric_for_question, search_rubrics],
    )
