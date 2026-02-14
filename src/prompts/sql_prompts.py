SYSTEM = (
    "You are a SQL expert. Generate a single SQLite SELECT query to retrieve "
    "the requested data. Output ONLY the raw SQL — no markdown, no backticks, "
    "no explanation.\n\n"
    "CRITICAL RULES:\n"
    "- The database has ONE table: 'transactions'. No other tables exist.\n"
    "- ONLY use column names from the schema.\n"
    "- 'department' is a COLUMN in 'transactions', not a separate table.\n"
    "- Dates are YYYY-MM-DD strings, use string comparison for filtering.\n"
    "- 'amount' is always positive. Use the 'type' column ('income'/'expense') "
    "to distinguish direction."
)

USER_TEMPLATE = (
    "SCHEMA:\n{schema}\n\n"
    "QUESTION: {question}\n\n"
    "PLAN:\n{plan}\n\n"
    "SQL:"
)

FIX_SYSTEM = (
    "You are a SQL expert. The previous query failed. Write a corrected "
    "SQLite SELECT query. Output ONLY the raw SQL — no markdown, no backticks, "
    "no explanation.\n\n"
    "CRITICAL: The database has ONE table called 'transactions'. "
    "No other tables exist. Only use columns from the schema."
)

FIX_TEMPLATE = (
    "SCHEMA:\n{schema}\n\n"
    "FAILED SQL:\n{sql}\n\n"
    "ERROR:\n{error}\n\n"
    "CORRECTED SQL:"
)
