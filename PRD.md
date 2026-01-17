# Product Requirements Document (PRD)
## WealthWise AI - Tax Intelligence Platform
*The "Vibe Coding" Personal Tax Auditor*

**Document Version**: 2.1
**Last Updated**: January 17, 2026
**Status**: Beta / Production Ready
**Owner**: Sid Viscious (Antigravity Team)

---

## 1. Executive Summary

**WealthWise AI** is an intelligent, privacy-first tax auditing platform. Unlike traditional tax filing software that acts as a passive form-filler, WealthWise AI functions as an **Active Guardian**. It ingests raw financial documents (PDFs, images), automates line-item audit using clustering AI, and employs a deterministic tax engine to simulate "Old vs New" regime outcomes with professional accuracy.

### Key Differentiators
- **Cyber-Finance Aesthetic**: Premium, dark-mode "Vibe Coding" UI built with Shadcn/UI & Tailwind.
- **Guardian Architecture**: Specialized micro-agents (SalarySentinel, HustleShield) for targeted analysis.
- **Cluster Review**: "Tinder-style" bulk classification of transactions (300 items audited in <3 mins).
- **Hybrid RAG**: Combines deterministic math (Calculator) with semantic legal search (ChromaDB).

---

## 2. Technical Architecture

### 2.1 Technology Stack
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion, Shadcn/UI, Lucide Icons.
- **Backend**: FastAPI (Python 3.11), Uvicorn.
- **Data Engineering**: Pandas, NumPy.
- **AI/ML**:
    - **Tier 1 Extraction**: Regex & PDFPlumber (Deterministic).
    - **Tier 2 OCR**: LayoutParser & Tesseract (Local).
    - **Tier 3 Vision**: Google Cloud Vision (Complex Scans).
    - **RAG**: ChromaDB (Vector Store) + `all-MiniLM-L6-v2` (Embeddings).

### 2.2 Core Modules
1.  **Ingestion Pipeline (`api/ingestion/`)**:
    -   **Router**: Directs files to valid parsers (Salary vs Bank vs Investments).
    -   **Scrubber**: Removes PII (names, account numbers) *before* processing.
    -   **Parsers**: Specialized logic for HDFC, ICICI, Form 16.
2.  **Tax Engine (`api/engine/`)**:
    -   **Calculator**: FY 2025-26 Slabs, Surcharge, Cess.
    -   **Deductions**: Logic for 80C, 80D, 80CCD, HRA (Metro/Non-Metro).
    -   **Capital Gains**: Budget 2024 rules (12.5% LTCG, 20% STCG).
3.  **Retrieval System (`api/engine/vector_store.py`)**:
    -   Indexes ~5MB of Income Tax Act JSONL.
    -   **Query Router**: Distinguishes between "Calculate tax" and "What is Section 80C?".

---

## 3. User Flows

### 3.1 The "Tunnel" (Onboarding)
- **Goal**: Context setting without friction.
- **Steps**:
    1.  **Persona**: Salaried, Freelancer, or Business?
    2.  **Guardians**: Select active agents (e.g., enable "WindfallWarden" for crypto).
    3.  **Upload**: Drag & drop files into "Zones" (Salary, Bank, Investments).

### 3.2 Ingest & Parse
- **Real-time Feedback**: File upload progress -> "Analyzing..." -> "Extracted 152 txns".
- **Validation**: backend validates PDF integrity and parsing confidence.

### 3.3 Cluster Review
- **Problem**: Manually tagging 500 bank transactions is painful.
- **Solution**:
    -   **Clustering**: Groups similar txns (e.g., "UBER RIDES").
    -   **UI**: Card stack interface. User clicks "Personal" once to tag 50 transactions.
    -   **Persistence**: Tags saved to backend memory for final calculation.

### 3.4 The Cockpit (Dashboard)
-   **Regime Showdown**: Side-by-side bar chart of Old vs New Regime tax liability.
-   **Rent Optimizer**: Slider to simulate "What if I pay ₹X rent?" -> live updates HRA exemption.
-   **Guardian Insights**: Cards showing specific savings (e.g., "Save ₹12k by declaring business expenses under 44ADA").

---

## 4. API Specification

### 4.1 Ingestion
- `POST /ingest/upload`: Multipart upload of PDFs. Returns `task_id`.
- `GET /ingest/status/{task_id}`: Polling for parsing completion.

### 4.2 Review
- `GET /review/transactions`: Returns list of parsed transactions.
- `POST /review/save`: Submits user classifications.

### 4.3 Analysis & RAG
- `POST /analysis`: Runs Guardians on full financial context. Returns `insights` and `potential_savings`.
- `POST /chat`: RAG endpoint. Accepts natural language query, returns answer + citations.

---

## 5. Roadmap

### Phase 1: MVP (Completed)
- [x] Basic parsing (Bank/Salary).
- [x] Tax Engine (Slabs, HRA, Caps Gains).
- [x] Dashboard UI with "Regime Showdown".
- [x] RAG Setup (ChromaDB).

### Phase 2: Intelligence (Current)
- [ ] Connect LLM (OpenAI) to RAG for conversational answers.
- [ ] Historical Comparison (Year-on-Year analysis).
- [ ] Export to JSON (ITR Prep).

### Phase 3: Production
- [ ] Dockerization.
- [ ] User Authentication (Supabase/Auth0).
- [ ] Persistent Database (PostgreSQL) replacing in-memory stores.

---

## 6. Success Metrics
- **Accuracy**: 100% deterministic match with manual Excel calculation for Salary Tax.
- **Speed**: <5 seconds to parse a 10-page bank statement.
- **Engagement**: Users completing "Cluster Review" in <2 minutes.
