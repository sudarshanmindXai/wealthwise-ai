# Changelog

All notable changes to WealthWise AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-01-16

### 🎉 Major Release - Document Intelligence & Production Ready

#### Added

##### Document Intelligence System
- **Universal Document Detector** - Auto-detect 20+ document types using GPT-4 Turbo
  - Form 16, Bank Statements, P&L Statements, Rental Agreements
  - Investment Statements, Home Loan Certificates, Capital Gains Statements
  - And 15+ more document types
- **GPT-4 Vision Extraction** - Intelligent data extraction from complex PDF layouts
  - Field-level confidence scoring (High/Medium/Low)
  - Full provenance tracking (source, timestamp, confidence)
  - User verification and editing interface
- **Multi-Document Upload** - Process multiple documents simultaneously
- **Extraction UI** - Dark-themed verification interface with audit trail

##### Core Features
- **Tax Regime Recommendation** - Compare Old vs New regime with personalized analysis
- **ITR Form Selection** - Automatic detection of correct ITR form (ITR-1 through ITR-7)
- **Scenario Planning Engine** - "What-if" analysis for tax-saving investments
- **Conversational Chat** - Natural language Q&A about tax rules and planning
- **Missing Info Detection** - Identify required vs optional data for accurate calculations

##### API Endpoints
- `POST /tax/recommendation` - Tax analysis (v1 & v2 compatible)
- `POST /tax/scenarios` - Scenario generation
- `POST /tax/chat` - Conversational assistant

##### UI/UX
- **Progressive Disclosure** - Staged form with 3-step workflow
- **Dark Mode Design System** - Finance-grade Vault Navy theme
- **Responsive Layout** - Works on desktop and tablet
- **Real-time Validation** - Input validation and helpful error messages
- **Audit Panel** - View extraction provenance for all fields

##### Infrastructure
- **Normalization Agent** - Resolve conflicts between manual input and extracted data
- **Audit Logger** - Complete request/response logging
- **Request Logging Middleware** - Debugging and performance monitoring
- **Safety Guardrails** - Domain checking and compliance-safe language

#### Changed
- Migrated from v1 (TaxProfile) to v2 (TaxProfileV2) request format
- Enhanced TaxFacts model with provenance tracking
- Improved error handling and validation
- Optimized tax computation engine for performance

#### Fixed
- Tax calculation edge cases for specific deduction combinations
- ITR-2 vs ITR-3 selection logic for business income
- Missing info detector false positives

#### Documentation
- Comprehensive README with installation and usage guides
- Quick Start Guide for 5-minute setup
- Document Ingestion Guide with 20+ examples
- API documentation with request/response samples
- UI Redesign Summary with design system guidelines
- User Journey Flow with state diagrams

#### Testing
- Unit tests for all core modules
- Integration tests for API endpoints
- Scenario tests for tax engine
- Smoke tests for quick validation

---

## [1.0.0] - 2025-12-01

### 🎯 Initial Release - Deterministic Tax Engine

#### Added
- **Deterministic Tax Computation** - Rule-based Old & New regime calculations
- **ITR Selector** - Logic for ITR-1, ITR-2, ITR-3, ITR-4 selection
- **Regime Recommender** - Compare regimes and recommend optimal choice
- **Basic UI** - Streamlit interface for manual data entry
- **RAG-lite Retrieval** - Keyword-based search in knowledge base
- **LLM Explanations** - Natural language explanations using GPT-4 Turbo
- **Knowledge Base** - JSONL format with Income Tax Act, Rules, ITR instructions

#### Core Principles Established
- LLMs for language only, NOT calculations
- Deterministic tax logic (auditable)
- No embeddings or vector databases
- Full audit trail for compliance

---

## Versioning Strategy

### Version Number Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes or major feature additions
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and minor improvements

### Release Schedule

- **Major releases**: Quarterly (v2.0, v3.0, etc.)
- **Minor releases**: Monthly (v2.1, v2.2, etc.)
- **Patch releases**: As needed (v2.0.1, v2.0.2, etc.)

---

## Upcoming Releases

### [2.1.0] - Planned Q2 2026

#### Planned Features
- Multi-document conflict resolution (Form 16 vs manual entry)
- Advanced validation rules engine
- Bulk document processing (entire folder upload)
- Historical tax comparison (year-over-year)
- Export to JSON for ITR pre-filling
- Enhanced scenario ranking algorithm

### [3.0.0] - Planned Q4 2026

#### Planned Features
- ITR form pre-filling (full XML export)
- Direct e-filing portal integration
- Multi-year tax planning dashboard
- Tax calendar with deadline reminders
- Family tax planning (multi-user)
- Mobile app (React Native)

---

## Links

- [GitHub Repository](https://github.com/yourusername/wealthwise-ai)
- [Documentation](https://github.com/yourusername/wealthwise-ai/tree/main/docs)
- [Issue Tracker](https://github.com/yourusername/wealthwise-ai/issues)
- [Discussions](https://github.com/yourusername/wealthwise-ai/discussions)

---

**[Unreleased]** - Development in progress  
**[2.0.0]** - Current stable release  
**[1.0.0]** - Initial release
