# Product Requirements Document (PRD)
## WealthWise AI - Tax Intelligence Platform
*The "Vibe Coding" Personal Tax Auditor*

**Document Version**: 2.2
**Last Updated**: January 17, 2026
**Status**: Release Candidate 1 (RC1)
**Owner**: Sid Viscious (Antigravity Team)

---

## 1. Executive Summary

**WealthWise AI** is an intelligent, privacy-first tax auditing platform. Unlike traditional tax filing software that acts as a passive form-filler, WealthWise AI functions as an **Active Guardian**. It ingests raw financial documents (PDFs, images), automates line-item audit using clustering and LLM-powered verification, and employs a deterministic tax engine to simulate "Old vs New" regime outcomes with professional accuracy.

### Key Differentiators
- **Cyber-Finance Aesthetic**: Premium, dark-mode "Vibe Coding" UI built with Next.js, Shadcn/UI & Tailwind.
- **Guardian Architecture**: Specialized micro-agents (SalarySentinel, HustleShield, PortfolioArchitect, WindfallWarden) for targeted analysis.
- **Transaction Review**: "Tinder-style" rapid classification with keyboard shortcuts (B/P/G/U) and AI confidence scoring.
- **CA Companion**: Context-aware RAG chatbot that knows your specific financial data and acts as a personal tax expert.
- **Twin-Engine Audit**: Real-time side-by-side comparison of Old vs. New Regime tax liabilities.

---

## 2. Technical Architecture

### 2.1 Technology Stack
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion, Shadcn/UI, Lucide Icons.
- **Backend**: FastAPI (Python 3.11), Uvicorn.
- **Data Engineering**: Pandas, NumPy.
- **AI/ML**:
    - **Tier 1 Extraction**: Regex & PDFPlumber (Deterministic).
    - **Tier 2 OCR**: LayoutParser & Tesseract (Local).
    - **Tier 3 Vision**: GPT-4 Vision / Google Cloud Vision (Complex Scans).
    - **RAG**: ChromaDB (Vector Store) + `all-MiniLM-L6-v2` (Embeddings) + LLM (Reasoning).

### 2.2 Core Modules
1.  **Ingestion Pipeline (`api/ingestion/`)**:
    -   **Document Hub**: Block-based upload system for comprehensive document gathering.
    -   **Router**: Directs files to valid parsers (Salary, Bank, Investments).
    -   **Scrubber**: Removes PII (names, account numbers) *before* processing.
    -   **Parsers**: Specialized logic for HDFC, ICICI, Form 16, Capital Gains.
2.  **Tax Engine (`api/engine/`)**:
    -   **Calculator**: Deterministc FY 2025-26 Slabs, Surcharge, Cess.
    -   **Reasoning Layer**: Logic for Deductions (80C, 80D), HRA, and Capital Gains (Budget 2024 rules).
    -   **Guardians**:
        -   **SalarySentinel**: Verification of Form 16 vs Bank Credits.
        -   **PortfolioArchitect**: STCG/LTCG harvesting and loss set-off.
        -   **HustleShield**: Business expense auditing (44ADA).
        -   **WindfallWarden**: Crypto (115BBH) and high-value transaction monitoring.
3.  **CA Companion (`api/chat/`)**:
    -   **Context-Aware**: Injects user's calculated tax profile into the system prompt.
    -   **Tools**: Access to `recalculate_tax`, `search_tax_law` capabilities.
    -   **Safety**: Guardrails against tax evasion queries.

---

## 3. User Flows

### 3.1 The "Tunnel" (Onboarding & Ingest)
- **Goal**: Context setting and frictionless data collection.
- **Steps**:
    1.  **Persona**: Salaried, Freelancer, or Business?
    2.  **Guardian Selection**: Enable active agents based on profile (e.g., "WindfallWarden" for crypto users).
    3.  **Document Hub**: Visual, block-based upload interface. Visibility of all required documents at once.
    4.  **Verification**: GPT-4 Vision powered extraction review for "Low Confidence" data.

### 3.2 Transaction Review & Polish
- **Problem**: Manually tagging 500 bank transactions is painful/error-prone.
- **Solution**: "Review" Page (`/review`).
    -   **AI Confidence**: Auto-approve >90%, Review 60-90%, Manual <60%.
    -   **Shortcuts**: Keyboard driven workflow - **B**usiness, **P**ersonal, **G**ains, **U**nsure.
    -   **UX**: Mouse-clickable classification buttons, bulk actions, and progress tracking.

### 3.3 The Twin-Engine Dashboard
-   **Regime Showdown**: Live comparative bar chart of Old vs New Regime tax liability.
-   **Rent Optimizer**: Interactive slider for HRA planning ("What if I pay ₹X rent?").
-   **Actionable Insights**: Cards showing specific savings opportunities found by Guardians.
-   **Reports**: One-click generation of **Form 12BB** for employer submission.

---

## 4. API Specification

### 4.1 Ingestion
- `POST /ingest/upload`: Multipart upload of PDFs. Returns `task_id`.
- `GET /ingest/status/{task_id}`: Polling for parsing/extraction feedback.

### 4.2 Review
- `GET /review/transactions`: Returns list of transactions with AI confidence scores.
- `POST /review/save`: Submits user classifications and "Unsure" flags.

### 4.3 Reasoning & Audit
- `POST /audit/run`: Triggers selected Guardians on the full financial context.
- `POST /chat`: CA Companion endpoint. Accepts natural language query + context, returns safe advice + citations.
- `GET /report/form12bb`: Generates the PDF submission for employers.

---

## 5. Roadmap

### Phase 1: Foundation (Completed)
- [x] Deterministic Tax Engine (Calculator, Slabs).
- [x] Basic parsing integration.
- [x] RAG Setup (ChromaDB + Legal Docs).

### Phase 2: Guardians (Completed)
- [x] Salary Sentinel (Form 16 Analysis).
- [x] Active Agents implementation (HustleShield, etc.).
- [x] Crypto Loss Traps (115BBH).

### Phase 3: Interface & Experience (Completed)
- [x] Next.js 14 + Shadcn/UI "Vibe Coding" implementation.
- [x] "Tunnel" Navigation (Ingest -> Review -> Dashboard).
- [x] Transaction Review with Keyboard Shortcuts.
- [x] CA Companion Chatbot integration.

### Phase 4: Validation & Polish (Current)
- [ ] Comprehensive End-to-End Testing (`TEST_SCENARIOS.md`).
- [ ] Nielsen Heuristics final audit.
- [ ] Session persistence cleanup.
- [ ] Production Deployment (Docker/Vercel).

---

## 6. Success Metrics
- **Accuracy**: 100% deterministic match with manual Excel calculation for Salary Tax (within ₹10 tolerance).
- **Efficiency**: Users completing full audit flow in <10 minutes.
- **Engagement**: Transaction Review page handling >200 items without dropping off.
- **Safety**: CA Companion successfully refusing 100% of evasion-related queries.
