from dataclasses import dataclass, field

from src.agents import PlannerAgent, SQLAgent, ValidatorAgent, ResponseAgent
from src.tools.db_connector import FinancialDatabase
from src.tools.llm import OllamaLLM


@dataclass
class PipelineResult:
    answer: str
    plan: str
    sql: str
    raw_results: str
    success: bool
    error: str = ""


class Pipeline:
    """Orchestrates the multi-agent workflow: Plan -> SQL -> Validate -> Respond."""

    def __init__(self, db: FinancialDatabase, llm: OllamaLLM, max_retries: int = 3):
        self.db = db
        self.schema = db.get_schema()
        self.planner = PlannerAgent(llm)
        self.sql_agent = SQLAgent(llm)
        self.validator = ValidatorAgent(llm, db, max_retries)
        self.response_agent = ResponseAgent(llm)

    def run(self, question: str) -> PipelineResult:
        # Step 1: Plan
        plan = self.planner.run(question, self.schema)

        # Step 2: Generate SQL
        sql = self.sql_agent.run(question, self.schema, plan)

        # Step 3: Validate & execute (with auto-retry)
        final_sql, columns, rows = self.validator.run(sql, self.schema)
        raw_results = FinancialDatabase.format_results(columns, rows)

        if not columns and not rows:
            return PipelineResult(
                answer="Sorry, I couldn't generate a valid query for that question.",
                plan=plan,
                sql=final_sql,
                raw_results="No results.",
                success=False,
                error="All query attempts failed.",
            )

        # Step 4: Generate response
        answer = self.response_agent.run(question, final_sql, columns, rows)

        return PipelineResult(
            answer=answer,
            plan=plan,
            sql=final_sql,
            raw_results=raw_results,
            success=True,
        )
