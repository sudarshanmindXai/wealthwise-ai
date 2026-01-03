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
- doc_type (act | rules | finance_act | circular | notification)
- section (string)
- sub_section (string or null)
- ay (array of strings)
- text (string, clean legal text)

Example:
```json
{
  "doc_id": "it_act_115bac_1a",
  "doc_type": "act",
  "section": "115BAC",
  "sub_section": "(1A)",
  "ay": ["2024-25"],
  "text": "Notwithstanding anything contained in this Act..."
}