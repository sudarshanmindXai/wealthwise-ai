# WealthWise-AI — Data Contract (Phase 1)

This document defines the REQUIRED format for all incoming legal data.

---

## File 1: chunks.jsonl (MANDATORY)

Purpose:
Clean, section-wise legal text for retrieval (RAG).

Rules:
- One JSON object per line
- Each line represents ONE logical law chunk
- No PDFs, no HTML, no tables

Required fields:
- doc_id (string, unique)
- doc_type (itr_instruction | validation_rule | booklet | circular | act)
- itr_form (string, e.g. ITR-1, ITR-2, ITR-3, ITR-4; null if generic)
- ay (array of strings, e.g. ["2025-26"])
- section (string, logical section name)
- field (string or null, UI field reference if applicable)
- text (string, clean legal / instructional text)

Example:
```json

{
  "doc_id": "it_act_115bac_1a",
  "doc_type": "act",
  "itr_form": null,
  "ay": ["2024-25"],
  "section": "115BAC",
  "field": null,
  "text": "Notwithstanding anything contained in this Act..."
}
