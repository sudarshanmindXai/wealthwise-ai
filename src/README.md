High-level modules:

- **ingest/**        → document extraction & intelligent data ingestion (NEW in v2.0)
  - document_detector.py → Auto-detect document type from PDF (GPT-4 Turbo)
  - universal_extractor.py → Extract structured data using GPT-4 Vision
  - Universal extraction pipeline supporting 20+ document types
  - Provenance tracking (source, confidence, timestamp)
- compute/       → deterministic tax computation engine
- decision/      → ITR selection & rule-based reasoning
- retrieval/     → RAG-lite document lookup (rule & keyword scoped)
- explain/       → deterministic explanation generation
- llm/           → language adapter (no business logic)
- agent/         → intent routing & tool orchestration
- safety/        → domain & language guardrails
- api/           → FastAPI endpoints
- core/          → orchestration, logging, audit trail

Design principles:

- Deterministic over probabilistic for tax logic
- No embeddings or vector databases (intentional)
- No semantic retrieval for compliance-critical decisions
- LLMs used only for language generation and document extraction
- All numeric outputs are rule-based and auditable
- Document extraction uses GPT-4 Vision but all data is user-verifiable



Note: This system intentionally uses a RAG-lite approach instead of embeddings-based RAG,
as tax computation requires determinism, traceability, and regulatory explainability.

**Document Extraction:** While we use GPT-4 Vision for extracting data from documents,
all extracted values are flagged with confidence scores and require user verification
before being used in tax calculations. The extraction is a convenience feature, not a
source of truth for compliance.