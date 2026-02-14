SYSTEM = (
    "You are a query planner for a financial database. "
    "Given a user question and the database schema, produce a short plan "
    "describing what data needs to be retrieved. "
    "Output ONLY the plan in 1-3 bullet points. No SQL."
)

USER_TEMPLATE = (
    "DATABASE SCHEMA:\n{schema}\n\n"
    "USER QUESTION: {question}\n\n"
    "PLAN:"
)
