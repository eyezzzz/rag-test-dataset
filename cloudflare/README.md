# Cloudflare integration — not deployed

Validated design against Cloudflare documentation for [D1](https://developers.cloudflare.com/d1/worker-api/), [R2](https://developers.cloudflare.com/r2/get-started/workers-api/), [Vectorize](https://developers.cloudflare.com/vectorize/reference/client-api/) and [Wrangler bindings](https://developers.cloudflare.com/workers/wrangler/configuration/).

## Intended ingestion

1. Keep immutable upstream source snapshots in R2 `raw/<dataset>/<revision>/...`. Check upstream licenses before import.
2. Store reviewed versioned JSONL snapshots in R2 `curated/v1/...` (no PII from real customers).
3. Create dedicated D1 database, apply `migrations/0001_library.sql`, then run `scripts/export_d1.py` and load the resulting SQL locally first using Wrangler.
4. All examples/strategies begin as `pending_review`. Review editorially and change status to `approved` only after validation.
5. Embed only APPROVED **strategy descriptions** in a model appropriate for multilingual Brazilian Portuguese. Keep the exact model identifier, dimensions and model version with your index config. Create Vectorize with *that* model's dimension, and upsert vectors with strategy ID as vector ID.
6. Retrieve IDs from Vectorize; read strategy details from D1 with an `approved` check. Simple `examplesForIntent` works without embeddings.
7. Connect to the YuiSync agent by service binding/import when ready. Do NOT enable public endpoints for raw datasets.

## Configuration

`wrangler.example.jsonc` is only a binding example — replace placeholders with real resource IDs after creating resources. It is NOT a standalone complete Wrangler project.

**Do not execute D1 migration on the petshop transaction database without comparing schemas**. Use a separate database or namespace and migration tracking.

### Separation of responsibilities

- Conversation library: style, question asking, handling corrections, sales conversation structure.
- YuiSync tenant data: catalog, stock, prices, schedule, deliveries, customer details, policies, tool permissions.
- Tenant isolation is enforced by the existing YuiSync operational data layer — NEVER replace it with corpus similarity matches.

## Production gate

Only `quality_status='approved'` can be served by the helper. No existing records have that status. This starter does **not** currently make the agent sound more natural in production; it is an auditable source library awaiting integration.

No Cloudflare account resources were created or modified.
