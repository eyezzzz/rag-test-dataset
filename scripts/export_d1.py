#!/usr/bin/env python3
"""Output a D1-compatible SQL seed. Apply migration first; does not approve anything."""
import hashlib
import json
from validate import EXAMPLES, STRATEGIES, SOURCES, load_jsonl, validate

def sql(v):
    if v is None: return "NULL"
    if isinstance(v, int): return str(v)
    return "'" + str(v).replace("'", "''") + "'"

def insert(table, cols, values):
    return "INSERT OR REPLACE INTO " + table + " (" + ", ".join(cols) + ") VALUES (" + ", ".join(map(sql, values)) + ");"

def main():
    problems, _, _ = validate()
    if problems: raise ValueError("\n".join(problems))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
    out = ["-- Generated seed: includes pending_review examples, no production approvals.", "BEGIN TRANSACTION;"]
    for x in sources:
        out.append(insert("conversation_sources", ["id", "title", "source_url", "license", "attribution"],
            [x["id"], x["name"], x["url"], x["license"], x["copyright"]]))
    for x in load_jsonl(EXAMPLES):
        msg_json = json.dumps(x["messages"],ensure_ascii=False,separators=(",",":"))
        digest = hashlib.sha256(msg_json.encode("utf8")).hexdigest()
        out.append(insert("conversation_examples",
            ["id","source_id","source_subset","source_conversation_id","locale","domain","intent",
             "features_json","messages_json","source_customer_turn_indices_json","expected_tool",
             "split","quality_status","content_sha256"],
            [x["id"], x["source"]["dataset"], x["source"]["subset"],x["source"]["source_conversation_id"],
             x["locale"], x["domain"], x["intent"], json.dumps(x["features"],ensure_ascii=False),
             msg_json, json.dumps(x["source"]["source_customer_turn_indices"]), x["expected_tool"],
             x["split"],x["quality_status"],digest]))
    for x in load_jsonl(STRATEGIES):
        out.append(insert("conversation_strategies",
            ["id","locale","domain","title","description","triggers_json","example_ids_json",
             "quality_status","embedding_status","version"],
            [x["id"],x["locale"],x["domain"],x["title"],x["description"],
             json.dumps(x["trigger_intents"],ensure_ascii=False),
             json.dumps(x["examples"],ensure_ascii=False),x["quality_status"],"not_indexed",x["version"]]))
    out.append("COMMIT;")
    print("\n".join(out))

if __name__ == "__main__":
    main()
