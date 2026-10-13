#!/usr/bin/env python3
"""Validate provenance, schema consistency and dialogue examples; stdlib only."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data/adapted/taskmaster2-petshop.pt-BR.jsonl"
STRATEGIES = ROOT / "data/strategies/conversation-strategies.pt-BR.jsonl"
SOURCES = ROOT / "metadata/sources.json"
ALLOWED_TOOLS = {
  "catalog_search", "service_catalog_lookup", "appointment_availability", "human_handoff"
}

def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines() if line.strip()]

def validate():
    errors = []
    meta = json.loads(SOURCES.read_text(encoding="utf8"))
    sources = {s["id"] for s in meta["sources"]}
    examples = load_jsonl(EXAMPLES)
    ids = set()
    for n, x in enumerate(examples, 1):
        p = f"example line {n}"
        if x["id"] in ids: errors.append(f"{p}: duplicate ID")
        ids.add(x["id"])
        if x["locale"] != "pt-BR" or x["domain"] != "petshop": errors.append(f"{p}: invalid scope")
        if x["quality_status"] not in ("pending_review", "approved", "rejected"): errors.append(f"{p}: bad status")
        if x["split"] not in ("train", "validation", "test"): errors.append(f"{p}: bad split")
        if x["expected_tool"] not in ALLOWED_TOOLS: errors.append(f"{p}: unknown tool")
        if x["source"]["dataset"] not in sources: errors.append(f"{p}: missing source")
        if not x["source"].get("source_conversation_id") or not x["source"].get("source_git_blob_sha"): errors.append(f"{p}: missing provenance")
        src_turns = x["source"].get("source_customer_turn_indices", [])
        if not src_turns or src_turns != sorted(set(src_turns)): errors.append(f"{p}: invalid source turn indices")
        msgs = x["messages"]
        if len(msgs) < 4: errors.append(f"{p}: too few turns")
        for i, msg in enumerate(msgs):
            expected = "customer" if i % 2 == 0 else "assistant"
            if msg.get("role") != expected or not isinstance(msg.get("text"), str) or not msg["text"].strip():
                errors.append(f"{p}: invalid message at index {i}")
    strategies = load_jsonl(STRATEGIES)
    strategy_ids = set()
    for s in strategies:
        if s["id"] in strategy_ids: errors.append(f"duplicate strategy {s['id']}")
        strategy_ids.add(s["id"])
        if not s["examples"] or any(ref not in ids for ref in s["examples"]):
            errors.append(f"broken example reference in {s['id']}")
        if s["quality_status"] not in ("pending_review", "approved", "rejected"):
            errors.append(f"invalid status in {s['id']}")
    return errors, len(examples), len(strategies)

if __name__ == "__main__":
    errors, n, m = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {n} examples and {m} strategies validated (not quality-approved)")
