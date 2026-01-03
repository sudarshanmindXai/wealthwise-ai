# src

This folder contains ALL source code for WealthWise-AI.

High-level modules:
- ingest/     → parsing, chunking, embedding
- retrieval/  → vector search and filtering
- tax/        → deterministic tax computation logic
- llm/        → prompt + grounded answer generation
- api/        → FastAPI endpoints

Rules:
- No data files here
- No notebooks here
- No ad-hoc scripts at repo root