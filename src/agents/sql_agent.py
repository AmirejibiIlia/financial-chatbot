import re

from src.prompts import sql_prompts
from src.tools.llm import OllamaLLM


class SQLAgent:
    """Generates a SQL query from the question, schema, and plan."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm

    def run(self, question: str, schema: str, plan: str) -> str:
        user_prompt = sql_prompts.USER_TEMPLATE.format(
            schema=schema, question=question, plan=plan
        )
        raw = self.llm.generate(sql_prompts.SYSTEM, user_prompt)
        return self._extract_sql(raw)

    @staticmethod
    def _extract_sql(text: str) -> str:
        # Strip markdown code fences if present
        match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Otherwise take the whole output, strip backticks
        return text.strip().strip("`").strip()
