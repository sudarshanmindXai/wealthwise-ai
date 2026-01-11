High-level modules:

- compute/      → deterministic tax computation engine
- decision/     → ITR selection & rule-based reasoning
- retrieval/    → RAG-lite document lookup (rule & keyword scoped)
- explain/      → deterministic explanation generation
- llm/          → language adapter (no business logic)
- agent/        → intent routing & tool orchestration
- safety/       → domain & language guardrails
- api/          → FastAPI endpoints
- core/         → orchestration, logging, audit trail

Design principles:

- Deterministic over probabilistic for tax logic
- No embeddings or vector databases (intentional)
- No semantic retrieval for compliance-critical decisions
- LLMs used only for language generation
- All numeric outputs are rule-based and auditable



Note: This system intentionally uses a RAG-lite approach instead of embeddings-based RAG,
as tax computation requires determinism, traceability, and regulatory explainability.