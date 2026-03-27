# WealthWise AI - Directory Architecture
> **Stack**: Next.js (Frontend) + FastAPI (Backend) + Python (Logic)

---

## Strict Folder Structure

All code generation must follow this tree.

```
wealthwise/
├── 📄 PROJECT_REQUIREMENTS.md       # The Master PRD (The "What")
├── 📄 STRATEGY_CORE.md              # The Logic/Math Engine (The "How")
├── 📄 TAX_RULES_CONSTANTS.md        # The Truth (Hardcoded Tax Slabs)
├── 📄 TEST_SCENARIOS.md             # The Validation Exam
├── 📄 PROJECT_PLAN.md               # The Execution Schedule
│
├── 📁 backend/                      # Python API (FastAPI)
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 📁 endpoints/
│   │   │   │   ├── 📄 upload.py     # Handle file uploads (Form 16, PDFs)
│   │   │   │   ├── 📄 audit.py      # Trigger specific Guardians
│   │   │   │   └── 📄 report.py     # Generate Form 12BB PDF
│   │   │   └── 📄 main.py           # FastAPI Entry Point
│   │   │
│   │   ├── 📁 guardians/            # The 4 Agents (Logic Only)
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 sentinel_salary.py      # Agent 1: HRA, NPS, Regime
│   │   │   ├── 📄 architect_portfolio.py  # Agent 2: Buybacks, Harvesting
│   │   │   ├── 📄 shield_hustle.py        # Agent 3: 44ADA Eligibility
│   │   │   ├── 📄 warden_windfall.py      # Agent 4: Rent, Gifts, HUF
│   │   │   └── 📄 orchestrator.py         # Runs all guardians in parallel
│   │   │
│   │   ├── 📁 engine/               # Pure Math & RAG
│   │   │   ├── 📄 calculator.py     # DETERMINISTIC TAX MATH (No LLM)
│   │   │   ├── 📄 compliance.py     # Rules (e.g., Wash Sale check)
│   │   │   ├── 📄 rag_router.py     # LangGraph Orchestrator
│   │   │   ├── 📄 parser.py         # OCR Utilities (Form 16/Bank)
│   │   │   └── 📄 constants.py      # Tax constants (from TAX_RULES)
│   │   │
│   │   ├── 📁 generators/           # Output Generation
│   │   │   ├── 📄 form12bb.py       # Form 12BB PDF
│   │   │   └── 📄 report.py         # Optimization report
│   │   │
│   │   └── 📁 models/               # Pydantic Schemas
│   │       ├── 📄 user_profile.py   # User Data Model
│   │       ├── 📄 tax_report.py     # Output Schema
│   │       └── 📄 guardian.py       # Guardian findings schema
│   │
│   ├── 📁 data/
│   │   ├── 📁 legal_docs/           # PDF/MD files (Income Tax Act)
│   │   ├── 📁 synthetic/            # "Rohan" Test Data
│   │   └── 📄 glossary.json         # Tax Definitions (RAG Context)
│   │
│   ├── 📁 tests/
│   │   ├── 📁 unit/
│   │   │   ├── 📁 math_engine/      # Calculator tests
│   │   │   └── 📁 guardians/        # Guardian logic tests
│   │   ├── 📁 integration/
│   │   │   └── 📁 api/              # API endpoint tests
│   │   └── 📄 conftest.py           # Pytest fixtures
│   │
│   ├── 📄 requirements.txt
│   ├── 📄 requirements-dev.txt
│   ├── 📄 Dockerfile
│   └── 📄 .env
│
├── 📁 frontend/                     # Next.js + Tailwind + Shadcn
│   ├── 📁 app/
│   │   ├── 📁 dashboard/            # The Main Twin-View (Old vs New)
│   │   ├── 📁 onboarding/           # The "Persona Sieve" Wizard
│   │   └── 📄 layout.tsx
│   │
│   ├── 📁 components/
│   │   ├── 📁 ui/                   # Shadcn UI Components
│   │   ├── 📁 guardians/            # Guardian-specific Cards
│   │   │   ├── 📄 SalaryCard.tsx
│   │   │   ├── 📄 PortfolioCard.tsx
│   │   │   ├── 📄 HustleCard.tsx
│   │   │   └── 📄 WindfallCard.tsx
│   │   ├── 📁 visualizers/          # Charts (Regime Comparison)
│   │   └── 📁 modals/               # Human-in-Loop dialogs
│   │
│   ├── 📁 lib/
│   │   ├── 📄 api.ts                # Axios calls to FastAPI
│   │   └── 📄 utils.ts              # Helper functions
│   │
│   ├── 📁 store/                    # Zustand state management
│   │   ├── 📄 userStore.ts
│   │   ├── 📄 onboardingStore.ts
│   │   └── 📄 analysisStore.ts
│   │
│   ├── 📁 public/
│   ├── 📄 package.json
│   ├── 📄 tailwind.config.ts
│   └── 📄 next.config.js
│
└── 📄 README.md
```

---

## Key File Responsibilities

| File | Responsibility |
|------|----------------|
| `engine/calculator.py` | **THE TRUTH** - All tax math (slabs, surcharge, cess, rebate) |
| `engine/constants.py` | Mirror of `TAX_RULES_CONSTANTS.md` |
| `engine/compliance.py` | Wash Sale checks, Audit triggers |
| `engine/rag_router.py` | LangGraph orchestration for RAG pipeline |
| `guardians/orchestrator.py` | Parallel execution of all 4 guardians |
| `generators/form12bb.py` | PDF generation using ReportLab |

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `SalaryCard.tsx` |
| Python modules | snake_case | `sentinel_salary.py` |
| API routes | snake_case | `audit.py` |
| Constants | SCREAMING_SNAKE | `MAX_80C_LIMIT` |