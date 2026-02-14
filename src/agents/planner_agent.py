from src.prompts import planner_prompts
from src.tools.llm import OllamaLLM


class PlannerAgent:
    """Analyzes the user question and produces a retrieval plan."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm

    def run(self, question: str, schema: str) -> str:
        user_prompt = planner_prompts.USER_TEMPLATE.format(
            schema=schema, question=question
        )
        return self.llm.generate(planner_prompts.SYSTEM, user_prompt)
