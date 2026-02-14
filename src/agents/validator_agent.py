import re

from src.prompts import sql_prompts
from src.tools.db_connector import FinancialDatabase
from src.tools.llm import OllamaLLM


class ValidatorAgent:
    """Executes SQL and self-corrects on errors up to max_retries."""

    def __init__(self, llm: OllamaLLM, db: FinancialDatabase, max_retries: int = 3):
        self.llm = llm
        self.db = db
        self.max_retries = max_retries

    def run(self, sql: str, schema: str) -> tuple[str, list[str], list[tuple]]:
        """Returns (final_sql, columns, rows). On total failure returns empty results."""
        for _ in range(self.max_retries):
            try:
                columns, rows = self.db.execute(sql)
                return sql, columns, rows
            except Exception as e:
                sql = self._fix(sql, str(e), schema)

        return sql, [], []

    def _fix(self, sql: str, error: str, schema: str) -> str:
        user_prompt = sql_prompts.FIX_TEMPLATE.format(
            sql=sql, error=error, schema=schema
        )
        raw = self.llm.generate(sql_prompts.FIX_SYSTEM, user_prompt)
        return self._extract_sql(raw)

    @staticmethod
    def _extract_sql(text: str) -> str:
        match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip().strip("`").strip()
