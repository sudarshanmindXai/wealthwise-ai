# WealthWise-AI — Architecture Decisions

This file records key decisions made during development.
Do NOT delete entries. Append only.

---

## Decision 001: Project Structure
- All executable code lives under `src/`
- No scripts or logic in repo root

Reason:
Prevents confusion and enforces clean layering.

---

## Decision 002: Data Separation
- `data_processed/` → cleaned legal text (JSONL)
- `data_structured/` → numeric/structured computation data (JSON)

Reason:
RAG systems break when text and numbers are mixed.

---

## Decision 003: LLM Usage
- LLMs are used ONLY for explanation
- All tax computation is deterministic code

Reason:
Trust, correctness, and auditability.