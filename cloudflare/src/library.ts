/**
 * Portable helper for YuiSync Workers / Cloudflare Agents SDK.
 * Attach shared library bindings to whichever Worker consumes it.
 * No routes are exposed, no deployment, no access to per-tenant operational data.
 * Runtime access is LIMITED to approved examples/strategies.
 */
export interface LibraryEnv {
  CONVERSATION_LIBRARY_DB: D1Database;
  CONVERSATION_LIBRARY_VECTORS?: VectorizeIndex;
  CONVERSATION_LIBRARY_R2?: R2Bucket;
}
export interface LibraryExample {
  id: string;
  intent: string;
  messages: Array<{ role: "customer" | "assistant"; text: string }>;
  expectedTool: string;
}
export interface LibraryStrategy {
  id: string;
  title: string;
  description: string;
  exampleIds: string[];
}
type RawExample = {
  id: string;
  intent: string;
  messages_json: string;
  expected_tool: string;
};
type RawStrategy = {
  id: string;
  title: string;
  description: string;
  example_ids_json: string;
};

const safeTopK = (n: number) =>
  Number.isFinite(n) ? Math.max(1, Math.min(5, Math.floor(n))) : 3;

/** Fast intent lookup when no embeddings are available. No pending records. */
export async function examplesForIntent(
  env: LibraryEnv,
  intent: string,
  limit = 3
): Promise<LibraryExample[]> {
  if (!intent || intent.length > 128) return [];
  const rows = await env.CONVERSATION_LIBRARY_DB
    .prepare(
      "SELECT id, intent, messages_json, expected_tool FROM conversation_examples " +
      "WHERE locale = 'pt-BR' AND domain = 'petshop' AND quality_status = 'approved' " +
      "AND intent = ? ORDER BY id LIMIT ?"
    )
    .bind(intent, safeTopK(limit))
    .all<RawExample>();
  return (rows.results ?? []).map((x) => ({
    id: x.id, intent: x.intent, messages: JSON.parse(x.messages_json), expectedTool: x.expected_tool,
  }));
}

/**
 * Pass an embedding from the model used to BUILD the index.
 * Only returns strategy text for records approved in D1.
 * Never treat a retrieved style strategy as a business policy.
 */
export async function strategiesForVector(
  env: LibraryEnv,
  queryEmbedding: number[],
  topK = 3
): Promise<LibraryStrategy[]> {
  if (!env.CONVERSATION_LIBRARY_VECTORS || queryEmbedding.length === 0) return [];
  const matches = await env.CONVERSATION_LIBRARY_VECTORS.query(queryEmbedding, {
    topK: safeTopK(topK),
    returnMetadata: "none",
  });
  const ids = [...new Set((matches.matches ?? []).map((m) => m.id))];
  if (!ids.length) return [];
  const found = await Promise.all(
    ids.map((id) => env.CONVERSATION_LIBRARY_DB
      .prepare("SELECT id, title, description, example_ids_json FROM conversation_strategies " +
               "WHERE id = ? AND locale = 'pt-BR' AND domain = 'petshop' AND quality_status = 'approved'")
      .bind(id).first<RawStrategy>())
  );
  return found.filter((r): r is RawStrategy => Boolean(r)).map((r) => ({
    id: r.id, title: r.title, description: r.description,
    exampleIds: JSON.parse(r.example_ids_json),
  }));
}

/** Optional versioned snapshot read. Not intended for customer-facing endpoints. */
export async function getReviewedSnapshot(
  env: LibraryEnv,
  key: string
): Promise<string | null> {
  if (!env.CONVERSATION_LIBRARY_R2 || !/^curated\/v[0-9]+\/[a-zA-Z0-9._-]+\.jsonl$/.test(key))
    return null;
  const object = await env.CONVERSATION_LIBRARY_R2.get(key);
  return object ? object.text() : null;
}
