import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "financial.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "sample_data.csv")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

MAX_RETRIES = 3
