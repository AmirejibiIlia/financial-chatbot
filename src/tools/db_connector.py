import csv
import sqlite3
from contextlib import contextmanager


class FinancialDatabase:
    """SQLite financial database with CSV seeding."""

    def __init__(self, db_path: str, csv_path: str | None = None):
        self.db_path = db_path
        self._create_table()
        if csv_path:
            self._seed(csv_path)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _create_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    date        TEXT,
                    category    TEXT,
                    subcategory TEXT,
                    amount      REAL,
                    type        TEXT,
                    description TEXT,
                    department  TEXT
                )
            """)

    def _seed(self, csv_path: str) -> None:
        with self._connect() as conn:
            if conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] > 0:
                return
            with open(csv_path, newline="") as f:
                for row in csv.DictReader(f):
                    conn.execute(
                        "INSERT INTO transactions "
                        "(date,category,subcategory,amount,type,description,department) "
                        "VALUES (?,?,?,?,?,?,?)",
                        (
                            row["date"],
                            row["category"],
                            row["subcategory"],
                            float(row["amount"]),
                            row["type"],
                            row["description"],
                            row["department"],
                        ),
                    )
            conn.commit()

    def get_schema(self) -> str:
        with self._connect() as conn:
            cols = conn.execute("PRAGMA table_info(transactions)").fetchall()
            lines = ["Table: transactions", "Columns:"]
            lines.extend(f"  {c[1]} ({c[2]})" for c in cols)

            for label, query in [
                ("Categories", "SELECT DISTINCT category FROM transactions"),
                ("Subcategories", "SELECT DISTINCT subcategory FROM transactions"),
                ("Types", "SELECT DISTINCT type FROM transactions"),
                ("Departments", "SELECT DISTINCT department FROM transactions"),
            ]:
                values = [r[0] for r in conn.execute(query).fetchall()]
                lines.append(f"{label}: {values}")

            date_range = conn.execute(
                "SELECT MIN(date), MAX(date) FROM transactions"
            ).fetchone()
            lines.append(f"Date range: {date_range[0]} to {date_range[1]}")

        return "\n".join(lines)

    def execute(self, sql: str) -> tuple[list[str], list[tuple]]:
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed.")

        with self._connect() as conn:
            cur = conn.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()

        return columns, rows

    @staticmethod
    def format_results(columns: list[str], rows: list[tuple]) -> str:
        if not rows:
            return "No results."

        header = " | ".join(columns)
        body = "\n".join(" | ".join(str(v) for v in row) for row in rows[:100])
        result = f"{header}\n{body}"
        if len(rows) > 100:
            result += f"\n... ({len(rows)} total rows, first 100 shown)"
        return result
