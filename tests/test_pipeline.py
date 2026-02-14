import os
import tempfile
import unittest

from src.tools.db_connector import FinancialDatabase


class TestFinancialDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "sample_data.csv"
        )
        self.db = FinancialDatabase(self.tmp.name, csv_path)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_schema_contains_table(self):
        schema = self.db.get_schema()
        self.assertIn("transactions", schema)
        self.assertIn("department", schema)

    def test_select_query(self):
        columns, rows = self.db.execute(
            "SELECT COUNT(DISTINCT department) FROM transactions"
        )
        self.assertEqual(len(columns), 1)
        self.assertEqual(len(rows), 1)
        self.assertGreater(rows[0][0], 0)

    def test_rejects_non_select(self):
        with self.assertRaises(ValueError):
            self.db.execute("DROP TABLE transactions")

    def test_format_results(self):
        columns = ["dept", "total"]
        rows = [("Sales", 100000), ("HR", 50000)]
        text = FinancialDatabase.format_results(columns, rows)
        self.assertIn("Sales", text)
        self.assertIn("dept | total", text)

    def test_format_empty(self):
        text = FinancialDatabase.format_results([], [])
        self.assertEqual(text, "No results.")


if __name__ == "__main__":
    unittest.main()
