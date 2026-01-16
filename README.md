# WealthWise AI — Tax Intelligence Platform

> **Professional. Precise. Secure.**  
> AI-powered tax planning and compliance platform for Indian taxpayers

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**WealthWise AI** is a production-grade tax planning and compliance platform designed specifically for Indian taxpayers. It combines deterministic tax computation with AI-powered document intelligence to provide accurate, auditable tax recommendations.

### What Makes WealthWise Different?

✅ **Deterministic Tax Calculations** — All tax computations are rule-based and auditable (no LLM math)  
✅ **Intelligent Document Extraction** — GPT-4 Vision automatically extracts data from 20+ document types  
✅ **Multi-Regime Analysis** — Compare Old vs New tax regimes with personalized recommendations  
✅ **Scenario Planning** — "What-if" analysis for investments and deductions  
✅ **Complete Audit Trail** — Full provenance tracking for compliance and transparency  
✅ **Professional UI** — Dark mode finance-grade design system

---

## 🚀 Key Features

### 1. Tax Regime Recommendation
- **Smart Analysis**: Compare Old vs New tax regime based on your profile
- **Personalized Savings**: See exactly how much you can save
- **Detailed Breakdown**: Understand deductions, exemptions, and tax liability

### 2. ITR Form Selection
- **Automatic Detection**: Determines which ITR form (ITR-1 through ITR-7) you should file
- **Rule-Based Logic**: Based on income sources, residency status, and transactions
- **Compliance Ready**: Ensures you file the correct form

### 3. Document Intelligence (GPT-4 Vision)

**Supported Documents (20+ Types):**

| Category | Document Types |
|----------|---------------|
| **Salaried** | Form 16, Salary Slips, Bank Statements, Investment Certificates |
| **Business** | P&L Statements, Balance Sheets, Business Bank Statements, GST Returns |
| **Property** | Rental Agreements, Home Loan Certificates, Property Tax Receipts |
| **Investments** | Capital Gains Statements, Dividend Statements, Mutual Fund Reports |

**Features:**
- Auto-detect document type
- Extract structured data with GPT-4 Vision
- Confidence scoring for each field
- User verification and editing before applying

### 4. Scenario Planning
- Test "what-if" scenarios for tax-saving investments
- Ranked recommendations by potential savings
- Investment-specific guidance (80C, 80D, NPS, etc.)

### 5. Conversational Assistant
- Natural language queries about tax rules
- Context-aware responses with citations
- No advice language (compliance-safe)

### 6. Audit Trail & Provenance
- Every extracted value tagged with source, confidence, and timestamp
- Complete request logging for debugging
- User-verifiable data lineage

---

## 🏗️ Architecture

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Deterministic Tax Logic** | All computations are rule-based and auditable |
| **LLM for Language Only** | GPT models used for extraction and explanation, NOT calculations |
| **Universal Document Pipeline** | Single extraction engine for all document types |
| **Progressive Disclosure** | Staged form with optional document upload |
| **Dark Mode Native** | Finance-grade professional UI (Vault Navy theme) |
| **Compliance First** | No advice language, full audit trail, user-verifiable data |

### Technology Stack

```
┌─────────────────────────────────────────────────┐
│  Frontend: Streamlit (Dark Theme Design)       │
│  • Progressive disclosure UI                    │
│  • Document upload & verification               │
│  • Scenario planning interface                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Backend API: FastAPI                           │
│  • /tax/recommendation - Tax analysis           │
│  • /tax/chat - Conversational Q&A               │
│  • /tax/scenarios - What-if analysis            │
│  • Request logging & audit middleware           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Core Engines (Deterministic)                   │
│  • Tax Computation Engine (Old/New regime)      │
│  • ITR Selector (ITR-1 through ITR-7)           │
│  • Scenario Engine (Investment optimization)    │
│  • Missing Info Detector                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Document Intelligence (GPT-4 Vision)           │
│  • Document Type Detector (20+ types)           │
│  • Universal Extractor (structured data)        │
│  • Confidence Scoring & Provenance              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Knowledge Base (JSONL)                         │
│  • Income Tax Act & Rules                       │
│  • ITR Form Instructions (ITR-1 to ITR-7)       │
│  • Validation Rules & Circulars                 │
└─────────────────────────────────────────────────┘
```

### Tech Stack Details

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Streamlit 1.29.0
- **LLM**: OpenRouter (GPT-4 Turbo, GPT-4 Vision)
- **Document Processing**: PyPDF2, pdfplumber
- **Tax Engine**: Custom rule-based computation engine
- **Testing**: pytest, pytest-asyncio

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- OpenRouter API Key ([Get one here](https://openrouter.ai/))

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourorg/wealthwise-ai.git
   cd wealthwise-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenRouter API Key:**
   
   Edit `streamlit_app.py` and replace the API key:
   ```python
   OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
   ```

4. **Start the backend API:**
   ```bash
   cd src/api
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Launch the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Access the app:**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

---

## 📖 Documentation & Planning

> **📋 Product Requirements**: See [PRD.md](PRD.md) — Complete product specification (800+ lines)  
> **📚 Full Documentation Index**: See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) — Master reference guide  
> **📂 Detailed Guides**: See [docs/README.md](docs/README.md) for technical documentation  
> **🚀 Quick Start**: See [docs/QUICKSTART.md](docs/QUICKSTART.md) for 5-minute setup

### What's in PRD.md?
- Executive summary and vision
- Target audience and user personas
- Complete feature specifications
- Technical and functional requirements
- User stories and workflows
- Success metrics and KPIs
- Roadmap and release plan
- Architecture diagrams
- Risk assessment
- Full product specification

---

## 🎯 Usage Guide

### Basic Tax Calculation

1. **Enter Income Details** (Stage 1):
   - Assessment Year
   - Residential Status
   - Annual Salary
   - TDS Paid
   - Age

2. **Click "Get Tax Summary"** to see:
   - Recommended tax regime (Old vs New)
   - Tax liability comparison
   - Potential savings

### Document Upload (Optional)

3. **Upload Tax Documents**:
   - Click "Upload Documents" section (appears after Stage 1)
   - Select one or more PDF files
   - System automatically:
     - Detects document type (Form 16, Bank Statement, etc.)
     - Extracts relevant tax data using GPT-4 Vision
     - Shows extracted fields with confidence scores
     - Allows verification/editing before applying to form

4. **Review Extracted Data**:
   - Check confidence scores (Green = >80%, Yellow = 50-80%, Red = <50%)
   - Verify accuracy against original document
   - Click "Apply to Form" to auto-populate fields

### Advanced Features

5. **Scenario Planning**:
   - Enter deductions (80C, 80D, Home Loan Interest)
   - See real-time tax impact
   - Adjust investment amounts to optimize savings

6. **Chat Assistant**:
   - Ask questions like "Which regime is better for me?"
   - Get explanations for tax calculations
   - Learn about specific deductions

---

## 🔧 Configuration

### Feature Flags

Edit `streamlit_app.py`:

```python
# Enable/disable document upload
DOCUMENT_UPLOAD_ENABLED = True

# API Configuration
API_HOST = "localhost"
API_PORT = 8000
TIMEOUT_SECS = 30

# OpenRouter Configuration
OPENROUTER_API_KEY = "sk-or-v1-your-key"
```

### Supported Document Types

The system can detect and extract from 20+ document types. See [src/ingest/document_detector.py](src/ingest/document_detector.py) for the complete list.

---

## 📁 Project Structure

```
wealthwise-ai/
│
├── streamlit_app.py              # Frontend UI (Streamlit)
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Test configuration
├── CONTRIBUTING.md               # Contribution guidelines
├── CHANGELOG.md                  # Version history
├── .gitignore                    # Git ignore rules
│
├── docs/                         # 📚 Comprehensive documentation
│   ├── README.md                 # Documentation index
│   ├── QUICKSTART.md             # 5-minute setup guide
│   ├── DOCUMENT_INGESTION_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── UI_REDESIGN_SUMMARY.md
│   ├── USER_JOURNEY_FLOW.md
│   ├── VISUAL_FLOW_GUIDE.md
│   ├── V2_IMPLEMENTATION_PLAN.md
│   ├── DATA_CONTRACT.md
│   └── DECISIONS.md
│
├── src/                          # Backend source code
│   ├── api/                      # FastAPI endpoints
│   │   ├── app.py                # Main API application
│   │   └── schemas/              # Pydantic request/response models
│   │
│   ├── agent/                    # Intent routing & orchestration
│   │   ├── router.py             # Agent intent classifier
│   │   └── normalization_agent.py # Data normalization
│   │
│   ├── compute/                  # Tax computation engines
│   │   ├── tax_engine.py         # Old/New regime calculations
│   │   └── scenario_engine.py    # What-if scenario generation
│   │
│   ├── decision/                 # Rule-based decision logic
│   │   ├── itr_selector.py       # ITR form selection
│   │   ├── regime_recommender.py # Regime comparison
│   │   └── missing_info_detector.py # Data completeness check
│   │
│   ├── ingest/                   # Document intelligence
│   │   ├── document_detector.py  # Auto-detect document type
│   │   └── universal_extractor.py # GPT-4 Vision extraction
│   │
│   ├── retrieval/                # Knowledge base search
│   │   └── basic_retriever.py    # Keyword-based retrieval
│   │
│   ├── explain/                  # Explanation generation
│   │   └── explain_regime_choice.py
│   │
│   ├── llm/                      # LLM adapters
│   │   └── llm_adapter.py        # OpenRouter integration
│   │
│   ├── safety/                   # Compliance guardrails
│   │   └── guardrails.py         # Domain & language checks
│   │
│   ├── conversation/             # Chat memory
│   │   └── memory.py             # Conversation history
│   │
│   ├── core/                     # Core services
│   │   ├── taxfacts.py           # TaxFacts data model
│   │   ├── recommendation_service.py
│   │   ├── scenario_service.py
│   │   ├── audit_logger.py
│   │   └── logging_config.py
│   │
│   └── tests/                    # Unit & integration tests
│       ├── test_contracts.py
│       └── test_integration_tax_api.py
│
├── data/                         # Knowledge base
│   ├── knowledge/
│   │   ├── acts_rules/           # Income Tax Act & Rules
│   │   ├── itr/                  # ITR form instructions
│   │   └── validations/          # Validation rules
│   └── user_profiles/            # Sample profiles
│
├── test_scenarios.py             # Scenario tests
└── test_scenarios_smoke.py       # Smoke tests
```

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest src/tests/
```

### Run Integration Tests
```bash
pytest test_scenarios.py -v
```

### Test Document Extraction
```bash
python -c "
from src.ingest.document_detector import detect_document_type
result = detect_document_type('path/to/form16.pdf', openrouter_api_key='your-key')
print(result)
"
```

---

## 🎨 Design System

The UI follows a **finance-grade dark mode** design system:

### Color Palette
- **Vault Navy** (#0F172A): Background
- **Slate Glass** (#1E293B): Cards/containers
- **Net-Gain Green** (#10B981): Savings/positive actions
- **Leakage Red** (#EF4444): Tax liability/risks
- **Ledger White** (#F8FAFC): Primary text
- **Audit Grey** (#94A3B8): Secondary text

### Typography
- **Inter**: Headings (Professional authority)
- **Roboto**: Body text (Readable at small sizes)
- **JetBrains Mono**: Numbers/data (Financial precision)

See [UI_REDESIGN_SUMMARY.md](UI_REDESIGN_SUMMARY.md) for complete guidelines.

---

## 📊 API Documentation

### Tax Recommendation Endpoint

**POST** `/tax/recommendation`

```json
{
  "assessment_year": "2024-25",
  "salary_gross": 1500000,
  "deduction_80c": 150000,
  "age_category": "below_60"
}
```

**Response:**
```json
{
  "recommended_regime": "new",
  "old_regime": {
    "total_tax": 234000,
    "effective_rate": 15.6
  },
  "new_regime": {
    "total_tax": 195000,
    "effective_rate": 13.0
  },
  "savings": 39000
}
```

See [API_DOCS.md](src/api/README.md) for complete documentation.

---

## 🛡️ Security & Privacy

- **No Data Storage**: All computations are stateless
- **Client-Side Processing**: Documents processed in-memory, not saved
- **API Key Security**: OpenRouter key stored locally (not transmitted to our servers)
- **Audit Trail**: All extracted data includes source provenance

---

## 🗺️ Roadmap

### v2.0 (Current)
- ✅ Tax regime recommendation
- ✅ ITR form selection
- ✅ Document upload with GPT-4 Vision extraction
- ✅ Progressive disclosure UI
- ✅ Dark mode design system

### v2.1 (Planned)
- ⏳ Multi-document conflict resolution (e.g., Form 16 vs manual entry)
- ⏳ Bulk document processing (entire tax folder upload)
- ⏳ Historical data comparison (year-over-year)
- ⏳ Advanced scenarios (capital gains, foreign income)

### v3.0 (Future)
- 📋 ITR form pre-filling (JSON export)
- 📋 Direct e-filing integration
- 📋 Multi-user support (family tax planning)
- 📋 Mobile app (React Native)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

Quick start for contributors:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run `pytest` to ensure all tests pass
5. Submit a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and releases.

**Current Version**: 2.0.0 (January 2026)

---

## 🙏 Acknowledgments

- **Income Tax Department of India**: Official tax rules and ITR schemas
- **OpenRouter**: Multi-model LLM gateway
- **Streamlit**: Rapid prototyping framework

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourorg/wealthwise-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourorg/wealthwise-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/wealthwise-ai/discussions)

---

**Built with ❤️ for Indian taxpayers. Professional. Precise. Secure.**
