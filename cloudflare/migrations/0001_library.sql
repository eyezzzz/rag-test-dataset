-- Standalone Cloudflare D1 schema. Apply only to a dedicated library D1 or review collisions.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS conversation_sources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source_url TEXT NOT NULL,
  license TEXT NOT NULL,
  attribution TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_examples (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES conversation_sources(id),
  source_subset TEXT NOT NULL,
  source_conversation_id TEXT NOT NULL,
  locale TEXT NOT NULL,
  domain TEXT NOT NULL,
  intent TEXT NOT NULL,
  features_json TEXT NOT NULL,
  messages_json TEXT NOT NULL,
  source_customer_turn_indices_json TEXT NOT NULL,
  expected_tool TEXT NOT NULL,
  split TEXT NOT NULL CHECK (split IN ('train','validation','test')),
  quality_status TEXT NOT NULL CHECK (quality_status IN ('pending_review','approved','rejected')),
  content_sha256 TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_examples_approved_intent
  ON conversation_examples (locale, domain, intent, quality_status);

CREATE TABLE IF NOT EXISTS conversation_strategies (
  id TEXT PRIMARY KEY,
  locale TEXT NOT NULL,
  domain TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  triggers_json TEXT NOT NULL,
  example_ids_json TEXT NOT NULL,
  quality_status TEXT NOT NULL CHECK (quality_status IN ('pending_review','approved','rejected')),
  embedding_status TEXT NOT NULL DEFAULT 'not_indexed' CHECK (embedding_status IN ('not_indexed','indexed','failed')),
  version INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_strategy_status
  ON conversation_strategies(locale,domain,quality_status);
