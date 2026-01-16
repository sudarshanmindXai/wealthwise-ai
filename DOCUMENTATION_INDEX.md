# WealthWise AI — Complete Documentation Index

**Version**: 2.0.0  
**Last Updated**: January 16, 2026  
**Status**: Production Ready ✅

---

## 📑 Quick Navigation

### 🎯 Start Here
- **[README.md](README.md)** — Main project overview and quick start
- **[PRD.md](PRD.md)** — Complete Product Requirements Document

### 🚀 Getting Started
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — 5-minute setup guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Developer guidelines

### 📚 Comprehensive Documentation
- **[docs/README.md](docs/README.md)** — Documentation index
- **[CHANGELOG.md](CHANGELOG.md)** — Version history and releases

### 📋 Project Management
- **[PRD.md](PRD.md)** — Product specifications and roadmap
- **[PROJECT_CLEANUP_SUMMARY.md](PROJECT_CLEANUP_SUMMARY.md)** — Cleanup and organization summary

---

## 📂 File Structure

### Root Directory (Project Overview)

```
wealthwise-ai/
├── README.md                    ⭐ Start here - Main documentation
├── PRD.md                       📋 Product Requirements Document (COMPLETE)
├── CONTRIBUTING.md              🤝 Contribution guidelines
├── CHANGELOG.md                 📜 Version history
├── PROJECT_CLEANUP_SUMMARY.md   ✅ Project health report
├── .gitignore                   🔒 Git security rules
├── requirements.txt             📦 Python dependencies
├── pytest.ini                   🧪 Test configuration
├── streamlit_app.py             🎨 Frontend UI (1243 lines)
├── test_scenarios.py            ✔️ Integration tests
└── test_scenarios_smoke.py      ✔️ Smoke tests
```

### Documentation Folder (/docs)

```
docs/
├── README.md                            📚 Documentation index
├── QUICKSTART.md                        🚀 5-minute setup
├── DOCUMENT_INGESTION_GUIDE.md          📄 Document extraction (20+ types)
├── IMPLEMENTATION_SUMMARY.md            ✅ What was built in v2.0
├── UI_REDESIGN_SUMMARY.md               🎨 Design system evolution
├── USER_JOURNEY_FLOW.md                 🗺️ User workflows & flows
├── VISUAL_FLOW_GUIDE.md                 📊 Document upload visual guide
├── V2_IMPLEMENTATION_PLAN.md            🏗️ Architecture & design
├── DATA_CONTRACT.md                     📋 Data format specifications
└── DECISIONS.md                         ⚖️ Architecture decisions (append-only)
```

### Source Code (/src)

```
src/
├── api/                         🌐 FastAPI Backend
│   ├── app.py                   → Main API (555 lines)
│   └── schemas/                 → Pydantic models
├── agent/                       🤖 Intent Routing
│   ├── router.py                → Intent classifier
│   └── normalization_agent.py   → Data normalization
├── compute/                     🧮 Tax Engines
│   ├── tax_engine.py            → Tax calculations
│   └── scenario_engine.py       → Tax-saving scenarios
├── decision/                    ⚖️ Business Rules
│   ├── itr_selector.py          → ITR form selection
│   ├── regime_recommender.py    → Regime comparison
│   └── missing_info_detector.py → Data completeness
├── ingest/                      📄 Document Intelligence
│   ├── document_detector.py     → Auto-detect document type
│   └── universal_extractor.py   → GPT-4 Vision extraction
├── retrieval/                   🔍 Knowledge Base
│   └── basic_retriever.py       → Keyword-based search
├── explain/                     💬 Explanations
│   └── explain_regime_choice.py → Why recommendations
├── llm/                         🤖 LLM Adapters
│   └── llm_adapter.py           → OpenRouter integration
├── safety/                      🛡️ Guardrails
│   └── guardrails.py            → Domain & language checks
├── conversation/                💬 Chat Memory
│   └── memory.py                → Conversation history
├── core/                        ⚙️ Services
│   ├── taxfacts.py              → Data model
│   ├── recommendation_service.py → Orchestration
│   ├── scenario_service.py      → Scenario generation
│   ├── audit_logger.py          → Audit trail
│   ├── logging_config.py        → Logging setup
│   └── request_logging_middleware.py
└── tests/                       ✔️ Unit Tests
    ├── test_contracts.py
    └── test_integration_tax_api.py
```

### Data (/data)

```
data/
├── knowledge/                   📚 Knowledge Base (22 JSONL files)
│   ├── acts_rules/              → Income Tax Act & Rules (7 files)
│   ├── itr/                     → ITR Forms 1-7 (7 files)
│   └── validations/             → Validation Rules (8 files)
├── user_profiles/               👤 Sample Data
│   └── sample_profile_v1.json   → Example user profile
└── docs_manifest.json           📋 Knowledge base manifest
```

---

## 🎯 Documentation by Role

### For Users (Taxpayers)
1. **Start**: [README.md](README.md) — Understand what the app does
2. **Setup**: [docs/QUICKSTART.md](docs/QUICKSTART.md) — Get it running
3. **Learn**: [docs/DOCUMENT_INGESTION_GUIDE.md](docs/DOCUMENT_INGESTION_GUIDE.md) — Use document upload
4. **Explore**: [docs/USER_JOURNEY_FLOW.md](docs/USER_JOURNEY_FLOW.md) — Learn workflows

### For Developers
1. **Start**: [README.md](README.md) — Project overview
2. **Setup**: [docs/QUICKSTART.md](docs/QUICKSTART.md) — Development setup
3. **Understand**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md) — Architecture
4. **Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md) — Guidelines
5. **Reference**: [src/README.md](src/README.md) — Module details

### For Product Managers
1. **Specification**: [PRD.md](PRD.md) — Complete product spec
2. **Roadmap**: [PRD.md](PRD.md#roadmap--release-plan) — Version roadmap
3. **Metrics**: [PRD.md](PRD.md#success-metrics--kpis) — KPIs and metrics
4. **History**: [CHANGELOG.md](CHANGELOG.md) — Version history

### For Tax Professionals
1. **Overview**: [README.md](README.md) — What it does
2. **Accuracy**: [PRD.md](PRD.md#technical-requirements) — Requirements
3. **Features**: [docs/DOCUMENT_INGESTION_GUIDE.md](docs/DOCUMENT_INGESTION_GUIDE.md) — Extraction features
4. **Integration**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md) — Architecture

### For Decision Makers / Investors
1. **Executive Summary**: [PRD.md](PRD.md#executive-summary) — High-level overview
2. **Market**: [PRD.md](PRD.md#target-audience--user-personas) — Market opportunity
3. **Roadmap**: [PRD.md](PRD.md#roadmap--release-plan) — Growth plan
4. **Metrics**: [PRD.md](PRD.md#success-metrics--kpis) — Business KPIs
5. **Vision**: [PRD.md](PRD.md#product-vision--objectives) — Strategic vision

---

## 📖 Documentation Summaries

### README.md (Main Documentation)
**Purpose**: Project overview and quick reference  
**Length**: 500+ lines  
**Key Sections**:
- Overview and differentiators
- Features and capabilities
- Installation and setup
- Usage guide and workflows
- Project structure
- Testing guidelines
- API documentation
- Roadmap

### PRD.md (Product Requirements Document) ⭐ NEW
**Purpose**: Complete product specification  
**Length**: 800+ lines  
**Key Sections**:
- Executive summary
- Vision and objectives
- Target audience and personas
- Problem statement
- Core features and capabilities
- Technical requirements (FR/NFR)
- User stories and workflows
- Success metrics and KPIs
- Data requirements
- Constraints and assumptions
- Roadmap and releases
- Risk assessment
- Glossary
- Technical architecture
- Complete sign-off

### CONTRIBUTING.md (Developer Guidelines)
**Purpose**: Contributor onboarding  
**Length**: 200+ lines  
**Key Sections**:
- Code of conduct
- Development setup
- Bug reporting template
- Feature request template
- Development workflow
- Code style guidelines
- Testing guidelines
- Code review process
- Areas for contribution
- Debugging tips

### CHANGELOG.md (Version History)
**Purpose**: Track changes and releases  
**Key Content**:
- Version 1.0.0 (Foundation)
- Version 1.5.0 (Enhancements)
- Version 2.0.0 (Current - Production)
- Roadmap for v2.1, v3.0, etc.

### docs/QUICKSTART.md
**Purpose**: 5-minute setup guide  
**Key Sections**:
- Prerequisites
- Installation steps
- Configuration
- First test
- Document upload test

### docs/V2_IMPLEMENTATION_PLAN.md
**Purpose**: Architecture and design  
**Key Sections**:
- v1 summary
- v2 implementation details
- Component architecture
- Decision made rationale

### docs/DOCUMENT_INGESTION_GUIDE.md
**Purpose**: Document extraction system  
**Key Sections**:
- Features overview
- 20+ supported document types
- Extraction pipeline details
- Confidence scoring
- API usage examples

### docs/UI_REDESIGN_SUMMARY.md
**Purpose**: Design system evolution  
**Key Sections**:
- Before/after comparison
- Color palette
- Typography
- Component library
- Copy and tone guidelines

### docs/USER_JOURNEY_FLOW.md
**Purpose**: User experience flows  
**Key Sections**:
- Screen flow diagrams (Mermaid)
- State management
- User workflows
- Progressive disclosure

### docs/VISUAL_FLOW_GUIDE.md
**Purpose**: Document upload visual guide  
**Content**: Step-by-step visual representation of workflows

### docs/DATA_CONTRACT.md
**Purpose**: Data format specifications  
**Key Sections**:
- JSONL format requirements
- Field definitions
- Validation rules

### docs/DECISIONS.md
**Purpose**: Architecture decisions (Append-only)  
**Key Decisions**:
- Project structure
- Data separation
- LLM usage policy

### PROJECT_CLEANUP_SUMMARY.md
**Purpose**: Project health and completion report  
**Key Content**:
- Completed tasks checklist
- Code quality metrics
- Testing status
- Recommendations for next steps

---

## 🔗 Cross-Reference Map

### By Topic

#### Tax Computation
- **How it works**: [README.md#architecture](README.md#-architecture) → [PRD.md#core-features](PRD.md#4-core-features--capabilities)
- **Implementation**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
- **Requirements**: [PRD.md#tax-regime-recommendation-engine](PRD.md#41-tax-regime-recommendation-engine)
- **Testing**: [test_scenarios.py](test_scenarios.py)

#### Document Extraction
- **Overview**: [README.md#document-intelligence](README.md#3-document-intelligence-gpt-4-vision)
- **Complete Guide**: [docs/DOCUMENT_INGESTION_GUIDE.md](docs/DOCUMENT_INGESTION_GUIDE.md)
- **Implementation**: [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)
- **Supported Types**: [PRD.md#supported-document-types](PRD.md#supported-document-types-20)
- **Code**: [src/ingest/](src/ingest/)

#### User Experience
- **Workflows**: [docs/USER_JOURNEY_FLOW.md](docs/USER_JOURNEY_FLOW.md)
- **Visual Guide**: [docs/VISUAL_FLOW_GUIDE.md](docs/VISUAL_FLOW_GUIDE.md)
- **Design System**: [docs/UI_REDESIGN_SUMMARY.md](docs/UI_REDESIGN_SUMMARY.md)
- **Requirements**: [PRD.md#user-stories--workflows](PRD.md#6-user-stories--workflows)

#### API
- **Overview**: [README.md#api-documentation](README.md#-api-documentation)
- **Endpoints**: [src/api/app.py](src/api/app.py)
- **Schemas**: [src/api/schemas/](src/api/schemas/)
- **Live Docs**: `http://localhost:8000/docs` (when running)

#### Architecture
- **Overview**: [README.md#architecture](README.md#-architecture)
- **Deep Dive**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
- **Decisions**: [docs/DECISIONS.md](docs/DECISIONS.md)
- **Requirements**: [PRD.md#technical-requirements](PRD.md#5-technical-requirements)
- **Diagram**: [PRD.md#technical-architecture-diagram](PRD.md#a-technical-architecture-diagram)

#### Deployment & Setup
- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Installation**: [README.md#installation](README.md#-installation)
- **Configuration**: [README.md#configuration](README.md#-configuration)
- **Testing**: [README.md#testing](README.md#-testing)

#### Product Management
- **Spec**: [PRD.md](PRD.md)
- **Roadmap**: [PRD.md#roadmap--release-plan](PRD.md#10-roadmap--release-plan)
- **Metrics**: [PRD.md#success-metrics--kpis](PRD.md#7-success-metrics--kpis)
- **Vision**: [PRD.md#product-vision--objectives](PRD.md#1-product-vision--objectives)
- **History**: [CHANGELOG.md](CHANGELOG.md)

#### Development
- **Setup**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
- **Code**: [src/](src/)
- **Tests**: [src/tests/](src/tests/)

---

## ✅ Checklist: What's Documented

### Product Definition
- ✅ [PRD.md](PRD.md) — Complete product specification
- ✅ [README.md](README.md) — Overview and quick reference
- ✅ Vision and objectives — [PRD.md#vision-statement](PRD.md#vision-statement)
- ✅ Target audience — [PRD.md#target-audience--user-personas](PRD.md#2-target-audience--user-personas)
- ✅ Features — [PRD.md#core-features--capabilities](PRD.md#4-core-features--capabilities)
- ✅ Requirements — [PRD.md#technical-requirements](PRD.md#5-technical-requirements)

### User Documentation
- ✅ Quick start — [docs/QUICKSTART.md](docs/QUICKSTART.md)
- ✅ User workflows — [docs/USER_JOURNEY_FLOW.md](docs/USER_JOURNEY_FLOW.md)
- ✅ Visual guide — [docs/VISUAL_FLOW_GUIDE.md](docs/VISUAL_FLOW_GUIDE.md)
- ✅ Features guide — [docs/DOCUMENT_INGESTION_GUIDE.md](docs/DOCUMENT_INGESTION_GUIDE.md)

### Technical Documentation
- ✅ Architecture — [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
- ✅ Implementation — [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)
- ✅ API docs — [README.md#api-documentation](README.md#-api-documentation)
- ✅ Data contract — [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)
- ✅ Design system — [docs/UI_REDESIGN_SUMMARY.md](docs/UI_REDESIGN_SUMMARY.md)

### Process Documentation
- ✅ Contributing — [CONTRIBUTING.md](CONTRIBUTING.md)
- ✅ Code style — [CONTRIBUTING.md#code-style](CONTRIBUTING.md#development-workflow)
- ✅ Testing — [CONTRIBUTING.md#testing-guidelines](CONTRIBUTING.md#-testing-guidelines)
- ✅ Code review — [CONTRIBUTING.md#code-review-process](CONTRIBUTING.md#-code-review-process)

### Project Management
- ✅ Roadmap — [PRD.md#roadmap--release-plan](PRD.md#10-roadmap--release-plan)
- ✅ Changelog — [CHANGELOG.md](CHANGELOG.md)
- ✅ Success metrics — [PRD.md#success-metrics--kpis](PRD.md#7-success-metrics--kpis)
- ✅ Risk assessment — [PRD.md#risk-assessment--mitigation](PRD.md#12-risk-assessment--mitigation)

### Decisions
- ✅ Architecture decisions — [docs/DECISIONS.md](docs/DECISIONS.md)
- ✅ Design decisions — [docs/UI_REDESIGN_SUMMARY.md](docs/UI_REDESIGN_SUMMARY.md)
- ✅ Data decisions — [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)

---

## 📞 How to Use This Index

### I want to... → Read this

| Goal | Document | Section |
|------|----------|---------|
| Understand the project | [README.md](README.md) | Overview & Features |
| Get it running | [docs/QUICKSTART.md](docs/QUICKSTART.md) | Setup |
| Understand how it works | [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md) | Architecture |
| Extract from documents | [docs/DOCUMENT_INGESTION_GUIDE.md](docs/DOCUMENT_INGESTION_GUIDE.md) | Features |
| Start development | [CONTRIBUTING.md](CONTRIBUTING.md) | Getting Started |
| Use the API | [README.md#api-documentation](README.md#-api-documentation) | Endpoints |
| Plan features | [PRD.md](PRD.md) | Requirements |
| Review changes | [CHANGELOG.md](CHANGELOG.md) | Version History |
| Understand design | [docs/UI_REDESIGN_SUMMARY.md](docs/UI_REDESIGN_SUMMARY.md) | Design System |
| Check project health | [PROJECT_CLEANUP_SUMMARY.md](PROJECT_CLEANUP_SUMMARY.md) | Status Report |

---

## 🎓 Learning Path

### For New Users (5-10 min)
1. Read [README.md](README.md) overview
2. Skim [docs/QUICKSTART.md](docs/QUICKSTART.md)
3. Try the app

### For Developers (1 hour)
1. Read [README.md](README.md)
2. Read [CONTRIBUTING.md](CONTRIBUTING.md)
3. Read [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
4. Browse [src/](src/) structure

### For Product Managers (30 min)
1. Read [PRD.md](PRD.md) executive summary
2. Review [PRD.md#roadmap--release-plan](PRD.md#10-roadmap--release-plan)
3. Check [PRD.md#success-metrics--kpis](PRD.md#7-success-metrics--kpis)
4. See [CHANGELOG.md](CHANGELOG.md)

### For Investors (15 min)
1. Read [PRD.md#executive-summary](PRD.md#executive-summary)
2. Review [PRD.md#target-audience--user-personas](PRD.md#2-target-audience--user-personas)
3. Check [PRD.md#success-metrics--kpis](PRD.md#7-success-metrics--kpis)
4. Skim [PRD.md#roadmap--release-plan](PRD.md#10-roadmap--release-plan)

---

## 🔍 Search Tips

### By Document Type
- **Specifications**: Look in [PRD.md](PRD.md)
- **Guides**: Look in `/docs`
- **Implementation**: Look in [src/](src/)
- **Changes**: Look in [CHANGELOG.md](CHANGELOG.md)
- **Guidelines**: Look in [CONTRIBUTING.md](CONTRIBUTING.md)

### By Topic
- **Features**: [PRD.md#core-features--capabilities](PRD.md#4-core-features--capabilities)
- **Architecture**: [docs/V2_IMPLEMENTATION_PLAN.md](docs/V2_IMPLEMENTATION_PLAN.md)
- **Design**: [docs/UI_REDESIGN_SUMMARY.md](docs/UI_REDESIGN_SUMMARY.md)
- **Data**: [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)
- **Users**: [PRD.md#target-audience--user-personas](PRD.md#2-target-audience--user-personas)

---

**Last Updated**: January 16, 2026  
**Status**: Complete ✅  
**Version**: 2.0.0

---

*For questions or feedback about documentation, please open an issue on GitHub.*
