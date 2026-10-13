"""Local tests; no external dependencies or network calls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate import validate, load_jsonl, EXAMPLES, STRATEGIES
from export_d1 import sql

class DatasetTests(unittest.TestCase):
    def test_schema(self):
        errors, examples, strategies = validate()
        self.assertEqual(errors, [])
        self.assertEqual(examples, 26)
        self.assertEqual(strategies, 8)

    def test_sources_and_style(self):
        examples = load_jsonl(EXAMPLES)
        origin_ids = {x["source"]["source_conversation_id"] for x in examples}
        self.assertEqual(len(origin_ids), 26)
        self.assertTrue(all(x["source"]["dataset"] == "google-taskmaster-2" for x in examples))
        self.assertTrue(all(x["quality_status"] == "pending_review" for x in examples))
        self.assertTrue(any("mudei de ideia" in m["text"].lower() for x in examples for m in x["messages"]))
        self.assertTrue(any("pera" in m["text"].lower() for x in examples for m in x["messages"]))
        
    def test_sql_escaping(self):
        self.assertEqual(sql("d'água"), "'d''água'")
        self.assertEqual(sql(None), "NULL")
        
    def test_strategy_examples_exist(self):
        keys = {x["id"] for x in load_jsonl(EXAMPLES)}
        for s in load_jsonl(STRATEGIES):
            self.assertTrue(set(s["examples"]).issubset(keys))

if __name__ == "__main__":
    unittest.main()
