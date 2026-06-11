"""Question bank retrieval sub-agent."""

from strands import Agent
from strands.models.openai import OpenAIModel

from app.config import get_settings
from app.tools.question_bank import search_question_bank

QUESTION_RETRIEVER_PROMPT = """
You are a question-bank retrieval specialist for mock interviews.

Use search_question_bank to find the most relevant interview questions for a
given job description and candidate resume. Prefer questions that match the
role's seniority, tech stack, and the candidate's experience gaps or strengths.

Return a concise summary listing the best matches with question_id, category,
difficulty, and the question text. Do not invent questions that are not in the bank.
""".strip()


def build_question_retriever_agent() -> Agent:
    settings = get_settings()
    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.interviewer_model,
        params={"max_tokens": 800, "temperature": 0.2},
    )
    return Agent(
        name="question_retriever",
        system_prompt=QUESTION_RETRIEVER_PROMPT,
        tools=[search_question_bank],
    )
