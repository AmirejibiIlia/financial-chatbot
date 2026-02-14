from src.prompts import response_prompts
from src.tools.db_connector import FinancialDatabase
from src.tools.llm import OllamaLLM


class ResponseAgent:
    """Generates a natural language answer from query results."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm

    def run(
        self,
        question: str,
        sql: str,
        columns: list[str],
        rows: list[tuple],
    ) -> str:
        results = FinancialDatabase.format_results(columns, rows)
        user_prompt = response_prompts.USER_TEMPLATE.format(
            question=question, sql=sql, results=results
        )
        return self.llm.generate(response_prompts.SYSTEM, user_prompt)
