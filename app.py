import streamlit as st

from src.config import CSV_PATH, DB_PATH, MAX_RETRIES, MODEL, OLLAMA_URL
from src.pipeline import Pipeline
from src.tools.db_connector import FinancialDatabase
from src.tools.llm import OllamaLLM


@st.cache_resource
def load_pipeline() -> Pipeline:
    db = FinancialDatabase(DB_PATH, CSV_PATH)
    llm = OllamaLLM(MODEL, OLLAMA_URL)
    return Pipeline(db, llm, MAX_RETRIES)


# ── Init ─────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Financial Analyst", page_icon="$", layout="wide")
st.title("Financial Analyst")
st.caption(
    "Multi-agent text-to-SQL — ask natural language questions about company finances."
)

pipeline = load_pipeline()

with st.sidebar:
    st.subheader("Schema")
    st.code(pipeline.schema, language="text")

# ── Chat ─────────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("plan"):
            with st.expander("Plan"):
                st.markdown(msg["plan"])
        if msg.get("sql"):
            with st.expander("SQL"):
                st.code(msg["sql"], language="sql")
        if msg.get("raw_results"):
            with st.expander("Raw results"):
                st.text(msg["raw_results"][:1000])

if question := st.chat_input("Ask a financial question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                result = pipeline.run(question)
            except Exception as e:
                result = None
                st.error(f"Error: {e}")

        if result:
            st.markdown(result.answer)
            with st.expander("Plan"):
                st.markdown(result.plan)
            with st.expander("SQL"):
                st.code(result.sql, language="sql")
            with st.expander("Raw results"):
                st.text(result.raw_results[:1000])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.answer,
                    "plan": result.plan,
                    "sql": result.sql,
                    "raw_results": result.raw_results,
                }
            )
