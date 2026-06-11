"""Interview orchestrator agent with sub-agents as tools."""

from dataclasses import dataclass
from typing import Any

from strands import Agent
from strands.models.openai import OpenAIModel

from app.agents.question_retriever import build_question_retriever_agent
from app.agents.rubric_specialist import build_rubric_specialist_agent
from app.config import get_settings

ORCHESTRATOR_PROMPT = """
You are the lead mock interview orchestrator.

You have two specialist sub-agents available as tools:
- question_retriever: searches the curated question bank for role-relevant questions
- rubric_specialist: retrieves scoring rubrics and evaluation criteria

When starting an interview:
1. Ask question_retriever for the best matching questions from the bank using the
   job description and resume.
2. Optionally ask rubric_specialist for rubric context on the strongest match.
3. Ask exactly ONE opening interview question tailored to the role and candidate.
   Prefer adapting a strong bank question; you may lightly rephrase for context.

Return only the final opening question text. No greeting, no explanation.
""".strip()

_orchestrator: Agent | None = None


@dataclass(frozen=True)
class OrchestratorResult:
    question: str
    tools_used: list[str]


def build_orchestrator_agent() -> Agent:
    settings = get_settings()
    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.interviewer_model,
        params={"max_tokens": 600, "temperature": 0.5},
    )
    question_retriever = build_question_retriever_agent()
    rubric_specialist = build_rubric_specialist_agent()

    return Agent(
        name="interview_orchestrator",
        model=model,
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[
            question_retriever,
            rubric_specialist,
        ],
    )


def get_orchestrator_agent() -> Agent:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = build_orchestrator_agent()
    return _orchestrator


def run_orchestrator(job_description: str, resume: str) -> OrchestratorResult:
    agent = get_orchestrator_agent()
    message_start = len(agent.messages)
    prompt = (
        "Start a mock interview.\n\n"
        f"JOB DESCRIPTION:\n{job_description.strip()}\n\n"
        f"RESUME:\n{resume.strip()}"
    )
    result = agent(prompt)
    tools_used = _extract_tools_used(agent.messages[message_start:])
    question = str(result).strip()
    return OrchestratorResult(question=question, tools_used=tools_used)


def _extract_tools_used(messages: list[dict[str, Any]]) -> list[str]:
    tools_used: list[str] = []
    seen: set[str] = set()

    for message in messages:
        for content in message.get("content", []):
            tool_use = content.get("toolUse") or content.get("tool_use")
            if not isinstance(tool_use, dict):
                continue
            name = (
                tool_use.get("name")
                or tool_use.get("toolName")
                or tool_use.get("tool_name")
            )
            if isinstance(name, str) and name not in seen:
                seen.add(name)
                tools_used.append(name)

    return tools_used
