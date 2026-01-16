# WealthWise AI — Documentation

Welcome to the comprehensive documentation for WealthWise AI.

---

## 📚 Documentation Index

### Getting Started

- **[Quick Start Guide](QUICKSTART.md)** — Get up and running in 5 minutes
  - Installation steps
  - First test with manual entry
  - Document upload walkthrough

### Architecture & Design

- **[V2 Implementation Plan](V2_IMPLEMENTATION_PLAN.md)** — Full architecture overview
  - Version 1 summary
  - Version 2 features and roadmap
  - Technical design decisions

- **[Data Contract](DATA_CONTRACT.md)** — Data format specifications
  - Required JSONL format for knowledge base
  - Field definitions and schema
  - Validation rules

- **[Architecture Decisions](DECISIONS.md)** — Key design decisions
  - Project structure rationale
  - Data separation approach
  - LLM usage policy

### Features & Implementation

- **[Document Ingestion Guide](DOCUMENT_INGESTION_GUIDE.md)** — Document extraction system
  - 20+ supported document types
  - GPT-4 Vision extraction pipeline
  - Confidence scoring and provenance
  - API usage examples

- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** — What was built in v2.0
  - Files created
  - Key features implemented
  - Document detection and extraction details

### User Experience

- **[UI Redesign Summary](UI_REDESIGN_SUMMARY.md)** — Design system evolution
  - Before/after comparison
  - Color palette and typography
  - Component library
  - Copy and tone guidelines

- **[User Journey Flow](USER_JOURNEY_FLOW.md)** — Screen flow analysis
  - State management with Streamlit
  - Visual flow diagrams (Mermaid)
  - User workflows and navigation

- **[Visual Flow Guide](VISUAL_FLOW_GUIDE.md)** — Document upload flow
  - Step-by-step visual guide
  - UI states and transitions
  - User feedback examples

---

## 🗂️ Quick Reference

### For Developers

| Topic | Documentation |
|-------|--------------|
| Setup & Installation | [QUICKSTART.md](QUICKSTART.md) |
| Architecture Overview | [V2_IMPLEMENTATION_PLAN.md](V2_IMPLEMENTATION_PLAN.md) |
| Design Decisions | [DECISIONS.md](DECISIONS.md) |
| Data Formats | [DATA_CONTRACT.md](DATA_CONTRACT.md) |

### For Feature Development

| Feature Area | Documentation |
|--------------|--------------|
| Document Extraction | [DOCUMENT_INGESTION_GUIDE.md](DOCUMENT_INGESTION_GUIDE.md) |
| Implementation Details | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) |
| UI/UX Guidelines | [UI_REDESIGN_SUMMARY.md](UI_REDESIGN_SUMMARY.md) |
| User Flows | [USER_JOURNEY_FLOW.md](USER_JOURNEY_FLOW.md) |

---

## 📖 Additional Resources

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs` (when backend is running)
- **ReDoc**: `http://localhost:8000/redoc`

### Code Documentation

- **[src/README.md](../src/README.md)** — Source code overview
- **[data/README.md](../data/README.md)** — Data folder structure

### Testing

- **[src/tests/README.md](../src/tests/README.md)** — Test suite documentation
- Root-level test files: `test_scenarios.py`, `test_scenarios_smoke.py`

---

## 🔄 Document Maintenance

### How to Update Documentation

1. **Add new features**: Update [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. **Change design**: Update [UI_REDESIGN_SUMMARY.md](UI_REDESIGN_SUMMARY.md)
3. **Add decision**: Append to [DECISIONS.md](DECISIONS.md) (never delete)
4. **Change data format**: Update [DATA_CONTRACT.md](DATA_CONTRACT.md)

### Documentation Principles

- ✅ Keep README.md in root folder as the main entry point
- ✅ Store detailed docs in `/docs` folder
- ✅ Never delete decision logs (append-only)
- ✅ Update version numbers in all relevant docs
- ✅ Include code examples wherever possible
- ✅ Use diagrams (Mermaid) for complex flows

---

## 📞 Support

If you can't find what you're looking for:

1. Check the [main README](../README.md)
2. Browse this documentation index
3. Look at inline code comments
4. Open an issue on GitHub

---

**Last Updated**: January 2026  
**Version**: 2.0
