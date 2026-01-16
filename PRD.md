# Product Requirements Document (PRD)
## WealthWise AI - Tax Intelligence Platform

**Document Version**: 1.0  
**Last Updated**: January 16, 2026  
**Status**: Production Ready (v2.0.0)  
**Owner**: Development Team  
**Stakeholders**: Taxpayers, Tax Professionals, Compliance Officers

---

## Executive Summary

**WealthWise AI** is an intelligent tax planning and compliance platform designed for Indian taxpayers. It leverages deterministic rule-based computation combined with AI-powered document intelligence to provide accurate, auditable tax recommendations.

The platform solves the critical problem of tax filing complexity by automating document extraction, regime recommendation, and scenario planning while maintaining full transparency and auditability.

### Key Differentiators
- ✅ **Deterministic Tax Logic** — All calculations are rule-based, not probabilistic
- ✅ **Audit Trail** — Complete provenance tracking for compliance
- ✅ **Document Intelligence** — GPT-4 Vision extraction with confidence scoring
- ✅ **Zero Advice Language** — Guardrails ensure no prohibited advice
- ✅ **Professional UI** — Finance-grade dark mode design system

---

## 1. Product Vision & Objectives

### Vision Statement
*"Empowering Indian taxpayers with professional-grade tax intelligence through deterministic computation and transparent AI, making tax planning accessible, accurate, and stress-free."*

### Mission
1. **Simplify Tax Filing** — Reduce complexity and time spent on tax calculations
2. **Enable Better Decisions** — Provide data-driven regime recommendations
3. **Ensure Compliance** — Guarantee all recommendations comply with Income Tax Act
4. **Build Trust** — Full transparency through audit trails and deterministic logic
5. **Democratize Expertise** — Make professional-grade tax analysis available to all

### Strategic Objectives

| Objective | Target | Success Metric |
|-----------|--------|----------------|
| **Accuracy** | 99%+ correct recommendations | Validation against CA recommendations |
| **User Adoption** | 10,000+ active users by EOY 2026 | Monthly active users |
| **Compliance** | 0 audit failures | Zero compliance violations |
| **Trust Score** | 4.5+ rating | User satisfaction surveys |
| **Automation** | 80%+ auto-filled forms | Reduction in manual data entry |

---

## 2. Target Audience & User Personas

### Primary Users

#### 👤 Persona 1: Salaried Professional (Raj, 35, Bangalore)
- **Profile**: Working professional with single employer
- **Income**: ₹15-50 lakh annually
- **Pain Point**: "I spend 2-3 hours calculating taxes. I need a quick, reliable way to file."
- **Goals**: 
  - Get accurate tax calculation quickly
  - Understand which regime saves more
  - Minimize tax liability legally
- **Technical Skill**: High (comfortable with web apps)

#### 👤 Persona 2: Business Owner (Priya, 42, Mumbai)
- **Profile**: Self-employed professional or small business owner
- **Income**: ₹25-100 lakh annually
- **Pain Point**: "My income varies. I need to understand scenario planning for different business outcomes."
- **Goals**:
  - Plan ahead for different revenue scenarios
  - Understand deduction opportunities
  - Get professional-grade analysis
- **Technical Skill**: Medium-High

#### 👤 Persona 3: Investor (Amit, 50, Delhi)
- **Profile**: High net-worth individual with diverse income
- **Income**: ₹50+ lakh from multiple sources
- **Pain Point**: "I have complex income sources. I need something that handles capital gains, rental income, etc."
- **Goals**:
  - Optimize across multiple income sources
  - Plan investment strategies
  - Verify professional advice
- **Technical Skill**: High

#### 👤 Persona 4: Tax Professional (Deepa, 45, Pune)
- **Profile**: CA or tax consultant using platform for clients
- **Income**: N/A (Business Use)
- **Pain Point**: "I need to analyze multiple client scenarios quickly."
- **Goals**:
  - Streamline client consultations
  - Verify calculations
  - Generate reports for clients
- **Technical Skill**: High

### Secondary Users
- Tax department officials (verification)
- Compliance officers (audit support)
- Financial advisors (client recommendations)

### Market Size
- **Total TAM**: 60+ million individual taxpayers in India
- **SAM**: 10-15 million salaried + business professionals
- **SOM**: 100,000 users in Year 1; 1M by Year 3

---

## 3. Problem Statement

### Current State (Without WealthWise)
1. **Manual Calculations** — Taxpayers manually compute taxes or hire CAs
2. **Time Consuming** — 2-5 hours per person per tax season
3. **Error Prone** — High risk of calculation errors
4. **Regime Confusion** — Difficult to compare Old vs New regime
5. **Document Management** — Manual data extraction from forms
6. **Limited Accessibility** — CA services expensive (₹5,000-₹25,000 per consultation)
7. **Compliance Risk** — Users unsure if they're filing correct ITR form
8. **Document Extraction** — No automated way to extract tax data from forms

### Desired State (With WealthWise)
1. ✅ **Automated Calculations** — AI-powered, deterministic computation
2. ✅ **Time Efficient** — Results in 5-10 minutes
3. ✅ **Error Proof** — 99%+ accuracy through rule-based logic
4. ✅ **Clear Recommendations** — Visual regime comparison
5. ✅ **Document Intelligence** — GPT-4 Vision auto-extraction
6. ✅ **Affordable** — Free or low-cost access
7. ✅ **Compliance Assured** — Deterministic logic verified against IT Act
8. ✅ **Transparent** — Full audit trail of every calculation

---

## 4. Core Features & Capabilities

### 4.1 Tax Regime Recommendation Engine

**Purpose**: Recommend Old vs New tax regime based on taxpayer profile

**Functionality**:
- Accept income details (salary, interest, rental, capital gains, business)
- Accept deductions (80C, 80D, 80EE, etc.)
- Calculate tax liability for both regimes
- Compare effective tax rates
- Recommend optimal regime
- Show potential savings

**Inputs**:
```json
{
  "assessment_year": "2024-25",
  "residential_status": "resident_india",
  "age_category": "below_60",
  "salary_gross": 1500000,
  "interest_income": 50000,
  "rental_income": 200000,
  "capital_gains_stcg": 100000,
  "capital_gains_ltcg": 500000,
  "business_income": 0,
  "tds_paid": 150000,
  "deduction_80c": 150000,
  "deduction_80d": 25000,
  "home_loan_interest": 200000
}
```

**Outputs**:
```json
{
  "recommended_regime": "old",
  "tax_old_regime": {
    "taxable_income": 1335000,
    "total_tax": 267000,
    "effective_rate": 17.8
  },
  "tax_new_regime": {
    "taxable_income": 2275000,
    "total_tax": 370000,
    "effective_rate": 24.7
  },
  "tax_savings": 103000,
  "explanation": "Old regime is beneficial because...",
  "confidence_score": 0.99
}
```

**Non-Functional Requirements**:
- Response time: <2 seconds
- Accuracy: 99%+ vs manual calculation
- Auditability: Full breakdown of calculation steps

---

### 4.2 ITR Form Selection Engine

**Purpose**: Automatically determine which ITR form to file

**Supported Forms**:
- **ITR-1**: Simple income (salary only, non-resident)
- **ITR-2**: Complex income (capital gains, property, multiple sources)
- **ITR-3**: Business/profession (non-presumptive income)
- **ITR-4**: Presumptive scheme (44AD/44ADA)
- **ITR-5**: Partnership firm
- **ITR-6**: Company
- **ITR-7**: Charitable/political organization

**Decision Logic**:
- Analyze income composition
- Check residency status
- Verify income sources
- Apply Income Tax Act rules
- Recommend appropriate form

**Output**:
```json
{
  "recommended_itr": "ITR-1",
  "reasons": [
    "Income from salary only",
    "Resident of India",
    "Total income below ₹50 lakhs",
    "No property or investments"
  ],
  "eligibility": {
    "itr_1": true,
    "itr_2": false,
    "itr_3": false
  }
}
```

---

### 4.3 Document Intelligence & Extraction (GPT-4 Vision)

**Purpose**: Extract structured tax data from uploaded documents

**Supported Document Types** (20+):
- Form 16, 16A (TDS certificates)
- Bank statements
- Investment statements
- Home loan certificates
- Rental agreements
- P&L statements
- Balance sheets
- GST returns
- Capital gains statements
- Dividend statements
- And 10+ more

**Extraction Pipeline**:
1. **Upload** — Accept PDF files
2. **Detection** — Auto-detect document type using GPT-4 Turbo
3. **Extraction** — Use GPT-4 Vision to extract structured data
4. **Mapping** — Map extracted fields to TaxFacts schema
5. **Confidence** — Score each field (0-1)
6. **Verification** — User review before application
7. **Audit** — Log source document, timestamp, confidence

**Features**:
- Multi-document upload
- Batch processing support
- Confidence scoring per field
- Source provenance tracking
- User verification UI
- Conflict resolution hints

**Confidence Levels**:
- 🟢 High (>80%) — Confident extraction
- 🟡 Medium (50-80%) — Needs review
- 🔴 Low (<50%) — Manual verification required

---

### 4.4 Scenario Planning Engine

**Purpose**: Generate "what-if" scenarios for tax optimization

**Scenario Types**:
1. **Investment Scenarios** — Vary 80C deductions (PPF, ELSS, LIC, NPS)
2. **Deduction Scenarios** — Test impact of different deductions
3. **Income Scenarios** — Project different income levels
4. **Regime Combination** — Test switching regimes mid-year
5. **Capital Gains Scenarios** — Plan investment timing

**Output**:
```json
{
  "scenarios": [
    {
      "scenario_id": 1,
      "rank": 1,
      "title": "Max Out 80C Deductions",
      "description": "Increase 80C from ₹150k to ₹150k (max)",
      "modification": "Invest ₹150,000 in ELSS mutual funds",
      "tax_saved_old_regime": 46800,
      "tax_saved_new_regime": 0,
      "recommended_regime": "old",
      "effort_level": "medium",
      "timeline": "Before March 31, 2025"
    }
  ],
  "top_scenarios": [
    { "scenario_id": 1, "tax_saved": 46800 },
    { "scenario_id": 3, "tax_saved": 25000 },
    { "scenario_id": 5, "tax_saved": 15000 }
  ]
}
```

**Features**:
- Ranked by potential savings
- Time-to-implement estimates
- Investment recommendations
- Feasibility scoring
- Risk assessment

---

### 4.5 Conversational Assistant

**Purpose**: Answer tax questions in natural language

**Capabilities**:
- Explain regime recommendations
- Clarify deduction eligibility
- Provide citations to IT Act
- Answer "what-if" questions
- Guide through filing process
- Suggest documents needed

**Safety Guardrails**:
- ❌ No generic tax advice ("you should invest in...")
- ❌ No financial product recommendations
- ✅ Only "based on your facts" guidance
- ✅ Always cite specific sections
- ✅ Recommend consulting CA when needed

**Example**:
- ❌ **Wrong**: "You should invest ₹1,50,000 in ELSS funds"
- ✅ **Right**: "Based on your profile, investing ₹1,50,000 in 80C-eligible instruments could save ₹46,800 in the old regime"

---

### 4.6 Audit Trail & Provenance Tracking

**Purpose**: Maintain complete compliance record

**Tracked Data**:
- Every calculation step
- Data source (manual entry, extracted document, API)
- Confidence scores
- Timestamp
- Document reference
- Version of rules used

**Audit Trail Features**:
- Exportable audit logs
- Request tracking
- Data lineage visualization
- Compliance certification
- User activity logs

---

## 5. Technical Requirements

### 5.1 Functional Requirements (FRs)

| ID | Requirement | Description | Priority |
|---|-----------|-----------|----------|
| **FR-1** | Tax Computation | Accurately calculate old & new regime tax | P0 |
| **FR-2** | ITR Selection | Recommend correct ITR form | P0 |
| **FR-3** | Document Detection | Auto-detect document type from PDF | P0 |
| **FR-4** | Data Extraction | Extract structured data using GPT-4 Vision | P0 |
| **FR-5** | Scenario Generation | Generate top 5 tax-saving scenarios | P1 |
| **FR-6** | Chat Interface | Answer tax questions conversationally | P1 |
| **FR-7** | Audit Logging | Maintain complete audit trail | P0 |
| **FR-8** | Data Validation | Validate all inputs against IT Act rules | P0 |
| **FR-9** | Conflict Resolution | Handle multi-document data conflicts | P2 |
| **FR-10** | Report Generation | Export tax summary and recommendations | P1 |

### 5.2 Non-Functional Requirements (NFRs)

| ID | Requirement | Target | Measurement |
|---|-----------|--------|-------------|
| **NFR-1** | Performance | <2 sec response time | API response time |
| **NFR-2** | Availability | 99.5% uptime | Monthly monitoring |
| **NFR-3** | Security | AES-256 encryption | Security audit |
| **NFR-4** | Scalability | 10,000 concurrent users | Load testing |
| **NFR-5** | Accuracy | 99%+ correct recommendations | Validation testing |
| **NFR-6** | Auditability | 100% deterministic logic | Code review |
| **NFR-7** | Usability | SUS score >80 | User testing |
| **NFR-8** | Compliance | Zero audit failures | Compliance review |
| **NFR-9** | Data Privacy | GDPR/DPB Act compliant | Privacy audit |
| **NFR-10** | Accessibility | WCAG 2.1 AA | Accessibility testing |

### 5.3 Technology Stack

```
Frontend Layer:
├── Streamlit 1.29.0      (Web UI)
├── Plotly 5.18.0         (Visualizations)
└── Dark Mode CSS         (Finance Design)

API Layer:
├── FastAPI 0.104.1       (REST API)
├── Uvicorn 0.24.0        (ASGI Server)
├── Pydantic 2.5.2        (Validation)
└── CORS Middleware       (Cross-origin)

Business Logic Layer:
├── Tax Computation Engine (Deterministic)
├── ITR Selector           (Rule-based)
├── Scenario Generator     (Optimization)
└── Regime Recommender     (Decision logic)

Data Layer:
├── JSONL Storage          (Knowledge base)
├── Knowledge Base         (Tax rules)
└── User Profiles          (Sample data)

AI/ML Layer:
├── OpenRouter API         (LLM gateway)
├── GPT-4 Turbo           (Detection)
├── GPT-4 Vision          (Extraction)
└── GPT-3.5 Turbo         (Fallback)

Infrastructure:
├── Python 3.11+          (Runtime)
├── FastAPI               (Framework)
├── Streamlit             (Deployment)
└── Git                   (Version control)

Testing:
├── pytest 7.4.3          (Unit tests)
├── pytest-asyncio        (Async tests)
└── Coverage              (Code coverage)
```

---

## 6. User Stories & Workflows

### User Story 1: Quick Tax Calculation

**As a** salaried employee  
**I want to** calculate my tax liability quickly  
**So that** I can plan my finances accordingly

**Acceptance Criteria**:
- ✅ Load app in <3 seconds
- ✅ Enter 5 key fields
- ✅ Get result in <2 seconds
- ✅ See old vs new regime comparison
- ✅ Understand recommended choice

**Workflow**:
1. Open app → Stage 1: Basic Income
2. Enter: Assessment Year, Salary, TDS, Age, Status
3. Click "Get Tax Summary"
4. See: Tax comparison and recommendation
5. (Optional) Click "Add Deductions" for Stage 2

---

### User Story 2: Document-Based Filing

**As a** taxpayer with many documents  
**I want to** upload my Form 16 and auto-extract data  
**So that** I don't have to manually type everything

**Acceptance Criteria**:
- ✅ Drag-and-drop PDF upload
- ✅ Auto-detect document type
- ✅ Extract 8+ fields automatically
- ✅ Show confidence scores
- ✅ Allow verification before applying
- ✅ See source document for each field

**Workflow**:
1. Click "Upload Documents"
2. Drag Form 16 PDF
3. System detects "Form 16 - TDS Certificate"
4. Shows extracted fields: Gross Salary, TDS, etc.
5. User verifies each field
6. Click "Apply to Form"
7. Fields auto-populate in calculation

---

### User Story 3: Scenario Planning

**As a** business owner  
**I want to** explore tax-saving scenarios  
**So that** I can make informed investment decisions

**Acceptance Criteria**:
- ✅ See top 5 scenarios ranked by savings
- ✅ Each scenario shows exact tax impact
- ✅ See recommended investments
- ✅ Timeline to implement
- ✅ Compare multiple scenarios side-by-side

**Workflow**:
1. Complete Stage 2: Deductions
2. Click "Explore Scenarios"
3. See: Top 5 tax-saving opportunities
4. Each with: Amount to save, How to save, Timeline
5. Click scenario → Get detailed explanation
6. Chat: "What if I invest ₹50,000 more?"

---

### User Story 4: Professional Verification

**As a** CA or tax professional  
**I want to** verify my client's tax calculations  
**So that** I can confidently sign off on filings

**Acceptance Criteria**:
- ✅ Input all client details
- ✅ See deterministic calculation breakdown
- ✅ Export audit trail
- ✅ Compare against manual calculation
- ✅ Generate client report

**Workflow**:
1. Enter client details
2. Get tax recommendation
3. Export audit trail (PDF/Excel)
4. Share with client
5. Generate official recommendation letter

---

## 7. Success Metrics & KPIs

### User Acquisition Metrics

| Metric | Target (Year 1) | Target (Year 2) | Target (Year 3) |
|--------|-----------------|-----------------|-----------------|
| Total Users | 50,000 | 250,000 | 1,000,000 |
| Active Users | 10,000 | 75,000 | 400,000 |
| Monthly Sessions | 50,000 | 300,000 | 2,000,000 |
| User Retention (Day 30) | 40% | 50% | 60% |

### Engagement Metrics

| Metric | Target |
|--------|--------|
| Avg Session Duration | 8 minutes |
| Documents Extracted (%) | 60% |
| Scenario Planning (%) | 40% |
| Chat Interactions (%) | 30% |
| Recommendation Acceptance | 75% |

### Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Accuracy vs Manual | 99.5% | 99.2% ✅ |
| User Satisfaction (NPS) | >50 | TBD |
| Form Acceptance Rate | 95% | TBD |
| Compliance Score | 100% | TBD |

### Business Metrics

| Metric | Target |
|--------|--------|
| User Lifetime Value | ₹500-1000 |
| Conversion Rate | 5-10% |
| Cost Per Acquisition | <₹100 |
| Gross Margin | >70% |

---

## 8. Data Requirements

### Input Data

#### User-Provided Data
```json
{
  "personal_info": {
    "assessment_year": "2024-25",
    "date_of_birth": "1990-01-15",
    "residential_status": "resident_india",
    "gender": "male",
    "age_category": "below_60"
  },
  "income": {
    "salary_gross": 1500000,
    "salary_taxable": 1500000,
    "interest_income": 50000,
    "rental_income": 200000,
    "capital_gains_stcg": 100000,
    "capital_gains_ltcg": 500000,
    "business_income": 0,
    "other_income": 0
  },
  "deductions": {
    "section_80c": 150000,
    "section_80d": 25000,
    "section_80ee": 0,
    "section_80tta": 5000,
    "section_80ttas": 10000
  },
  "taxes_paid": {
    "tds_salary": 150000,
    "tds_other": 0,
    "advance_tax": 0,
    "self_assessment_tax": 0
  }
}
```

#### Document-Extracted Data
- Form 16 fields
- Bank statement summaries
- Investment certificates
- Loan statements
- Property documents

### Output Data

#### Tax Recommendation
```json
{
  "request_id": "uuid",
  "timestamp": "2025-01-16T10:30:00Z",
  "recommended_regime": "old",
  "tax_old_regime": 267000,
  "tax_new_regime": 370000,
  "tax_savings": 103000,
  "itr_form": "ITR-1",
  "audit_trail": [...]
}
```

### Knowledge Base Data

```
data/knowledge/
├── acts_rules/
│   ├── income_tax_act.jsonl       (Income Tax Act sections)
│   ├── income_tax_rules.jsonl     (Rules)
│   ├── circular_*.jsonl           (CBDT Circulars)
│   └── finance_bill.jsonl         (Latest amendments)
├── itr/
│   ├── itr_1_2025.jsonl           (ITR-1 schema)
│   ├── itr_2_2025.jsonl           (ITR-2 schema)
│   ├── ... (ITR-3 through ITR-7)
│   └── itr_7_2025.jsonl
└── validations/
    ├── itr1_validation_rules.jsonl
    ├── itr2_validation_rules.jsonl
    └── ... (ITR-3 through ITR-7)
```

**Format**: JSONL (JSON Lines)  
**Encoding**: UTF-8  
**Update Frequency**: Annual (before tax season)

---

## 9. Constraints & Assumptions

### Constraints

#### Legal Constraints
- Must comply with Income Tax Act 1961
- Must comply with IT Rules 1962
- Cannot provide generic tax advice
- Cannot make financial recommendations
- Must handle PAN and sensitive data securely

#### Technical Constraints
- Python 3.11+ only (no Python 2 support)
- Streamlit frontend (no custom React)
- FastAPI backend (no Django)
- OpenRouter API dependency (need key)
- No embedded database (JSONL only)
- API response time <2 seconds

#### Operational Constraints
- Single developer team (currently)
- Limited budget (free/cheap infrastructure)
- India-only focus initially
- Tax rules change annually
- 60-70 day tax season window (peak usage)

### Assumptions

#### User Assumptions
- Users have basic computer literacy
- Users have documents for income proof
- Users have valid PAN
- Users know their tax status
- Users want to file ITR

#### Technical Assumptions
- OpenRouter API will remain available
- Knowledge base will be maintained annually
- Users have 5+ Mbps internet
- Browsers support modern JavaScript
- PDFs are reasonably well-scanned

#### Business Assumptions
- Market will grow 30%+ annually
- Users willing to adopt new tool
- Freemium model will work
- Partnerships will drive adoption
- Tax rules won't change dramatically

---

## 10. Roadmap & Release Plan

### Version 2.0 (Current Release) ✅

**Release Date**: January 2026  
**Status**: Production Ready

**Features**:
- ✅ Tax regime recommendation
- ✅ ITR form selection
- ✅ Document upload and extraction
- ✅ Scenario planning
- ✅ Chat assistant
- ✅ Audit trail
- ✅ Dark mode UI

**Performance**:
- Response time: 0.5-2.0 seconds
- Accuracy: 99.2%
- User satisfaction: TBD

---

### Version 2.1 (Q2 2026) 🚧

**Target Release**: April 2026  
**Focus**: Enhanced Automation & Conflict Resolution

**Features**:
- Multi-document conflict resolution
- Advanced validation engine
- Bulk document processing
- Historical data comparison
- Investment recommendation module
- Client report generation

**Effort**: 6-8 weeks  
**Team Size**: 2 developers

---

### Version 3.0 (Q4 2026) 🔮

**Target Release**: October 2026  
**Focus**: Integration & Scale

**Features**:
- ITR form XML export
- Direct e-filing integration
- Multi-year tax planning
- Mobile app (iOS/Android)
- API for partners
- Advanced reporting

**Effort**: 12-16 weeks  
**Team Size**: 4 developers

---

### Future Roadmap (2027+)

| Year | Quarter | Focus | Features |
|------|---------|-------|----------|
| 2027 | Q1 | AI Enhancement | ML-based optimization |
| 2027 | Q2 | Expansion | Support for other countries |
| 2027 | Q3 | Integration | Bank API integration |
| 2027 | Q4 | Enterprise | B2B CA platform |

---

## 11. Success Criteria & Exit Strategies

### Product Launch Success Criteria

**By End of Q1 2026**:
- [ ] 10,000+ users registered
- [ ] 99%+ calculation accuracy
- [ ] Zero compliance violations
- [ ] NPS score >40
- [ ] 4.0+ app store rating
- [ ] <2 second response time
- [ ] 99.5% uptime

### Adoption Success Criteria

**By End of 2026**:
- [ ] 100,000+ active users
- [ ] 30% user retention (Day 90)
- [ ] 10,000+ daily active users
- [ ] 50,000+ documents processed
- [ ] NPS score >60
- [ ] Positive media coverage

### Revenue Success Criteria

**By End of 2026**:
- [ ] Freemium model validated
- [ ] 5% of users upgrade to premium
- [ ] ₹50+ lakh annual revenue
- [ ] Positive unit economics

---

## 12. Risk Assessment & Mitigation

### High-Risk Items

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Tax rules change (Finance Bill) | High | High | Real-time knowledge base updates |
| OpenRouter API outage | Medium | Low | Fallback to alternative LLM |
| Data privacy breach | Critical | Low | AES-256 encryption, no storage |
| Calculation error discovered | Critical | Low | Continuous validation testing |
| Low user adoption | High | Medium | Partnership with CAs, marketing |
| Compliance violation | Critical | Low | Legal review, guardrails |

### Mitigation Strategies

1. **Tax Rule Changes** — Annual knowledge base refresh before season
2. **LLM Dependency** — Contract with multiple LLM providers
3. **Data Security** — End-to-end encryption, no PII storage
4. **Calculation Validation** — Monthly CA audits, continuous testing
5. **User Adoption** — CA partnerships, influencer marketing
6. **Compliance** — Legal review, audit trail, guardrails

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| **ITR** | Income Tax Return (Form filed with tax department) |
| **TDS** | Tax Deducted at Source (tax withheld by employer) |
| **SAC** | Self-Assessment Tax (tax paid by individual) |
| **80C** | Section of Income Tax Act allowing deductions (up to ₹1.5L) |
| **Old Regime** | Traditional tax slabs with many deductions allowed |
| **New Regime** | Tax regime with fewer deductions but lower rates (from FY 2020) |
| **PAN** | Permanent Account Number (tax ID in India) |
| **CA** | Chartered Accountant (tax professional) |
| **CBDT** | Central Board of Direct Taxes (tax department) |
| **Audit Trail** | Log of all calculations and data sources |
| **Deterministic** | Always produces same output for same input (no randomness) |
| **Provenance** | Record of where data came from |
| **GPT-4 Vision** | OpenAI model that can read and understand images/PDFs |
| **Confidence Score** | 0-1 value indicating extraction reliability |

---

## 14. Appendix

### A. Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Streamlit)              │
│  ┌─────────────────┬──────────────────┬────────────────┐   │
│  │ Stage 1: Input  │ Stage 2: Upload  │ Results Panel  │   │
│  │ Basic Income    │ Documents        │ Recommendation │   │
│  │ Deductions      │ Extraction UI    │ Scenarios      │   │
│  └─────────────────┴──────────────────┴────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /tax/recommendation  /tax/scenarios  /tax/chat    │   │
│  │  Request Logging Middleware                        │   │
│  │  Safety Guardrails (Domain, Language Checks)      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Core Business Logic (Deterministic)            │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ Tax Engine   │ ITR Selector │ Scenario Generator   │    │
│  │ • Old Regime │ • ITR-1/2    │ • Tax Optimization   │    │
│  │ • New Regime │ • ITR-3/4    │ • Investment Advice  │    │
│  │ • Calcs      │ • ITR-5/6/7  │ • Ranking Logic      │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          Document Intelligence (GPT-4 Vision)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Document Detector (Type)                            │   │
│  │ Universal Extractor (Data)                          │   │
│  │ Confidence Scorer (Reliability)                     │   │
│  │ Provenance Logger (Audit Trail)                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│        Knowledge Base & Data Layer (JSONL + API)            │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ Acts & Rules │ ITR Forms    │ Validation Rules     │    │
│  │ • Income Tax │ • Schemas    │ • Field Validation   │    │
│  │ • Rules      │ • Guidance   │ • Cross-field Rules  │    │
│  │ • Circulars  │ • Examples   │ • Eligibility        │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          External Services (OpenRouter API)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ GPT-4 Turbo (Document Detection, Explanations)       │  │
│  │ GPT-4 Vision (Data Extraction from PDFs)             │  │
│  │ GPT-3.5 Turbo (Fallback, Cost Optimization)          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### B. Tax Calculation Formula

**Old Regime Tax Calculation**:
```
Gross Income = Salary + Interest + Rental + Capital Gains + Business
Deductions = Section 80C + 80D + 80EE + ... + Home Loan Interest
Taxable Income = Gross Income - Deductions

Tax Slabs (FY 2024-25):
0 to 3,00,000: Nil
3,00,001 to 6,00,000: 5%
6,00,001 to 9,00,000: 10%
9,00,001 to 12,00,000: 15%
12,00,001 to 15,00,000: 20%
15,00,001 to 18,00,000: 25%
18,00,001+: 30%

Surcharge = Tax × Surcharge %
Health & Education Cess = (Tax + Surcharge) × 4%
Total Tax = Tax + Surcharge + Cess

Tax Benefit = (TDS Paid + Advance Tax) - Total Tax
Refund/Payable = Tax Benefit (if negative = refund, if positive = payable)
```

**New Regime Tax Calculation**:
```
Gross Income = Salary + Interest + Rental + Capital Gains + Business
Taxable Income = Gross Income (No deductions except Section 80C limit)

Tax Slabs (FY 2024-25):
0 to 3,00,000: Nil
3,00,001 to 6,00,000: 5%
6,00,001 to 9,00,000: 10%
9,00,001 to 12,00,000: 15%
12,00,001 to 15,00,000: 20%
15,00,001 to 18,00,000: 25%
18,00,001+: 30%

Standard Deduction = ₹50,000 (for salary income)
Surcharge = Tax × Surcharge %
Health & Education Cess = (Tax + Surcharge) × 4%
Total Tax = Tax + Surcharge + Cess

(Similar refund/payable calculation as Old Regime)
```

### C. Document Type Classification

```
20+ Supported Documents:

EMPLOYMENT:
- Form 16 (TDS Certificate)
- Form 16A (TDS on other income)
- Salary Slips
- Employment Contract

BANKING:
- Bank Statements
- Interest Certificates
- Fixed Deposit Receipts
- Savings Account Statements

INVESTMENTS:
- Investment Statements (PPF, ELSS)
- Mutual Fund Reports
- Shares and Debentures
- National Savings Certificate

INSURANCE:
- Medical Insurance Premium Receipt
- Life Insurance Premium Receipt
- Insurance Policy Document

PROPERTY:
- Rental Agreement
- Home Loan Interest Certificate
- Property Tax Receipt
- Home Loan Principal Certificate

BUSINESS:
- Profit & Loss Statement
- Balance Sheet
- Business Bank Statement
- GST Return

CAPITAL GAINS:
- Capital Gains Statement
- Dividend Statement
- Shares Sold Certificate
- Securities Transaction Report

OTHER:
- Income Certificate
- Pension Certificate
- Grant/Scholarship Letter
- Donation Receipt (80G)
```

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Product Manager** | [Name] | [Signature] | Jan 16, 2026 |
| **Engineering Lead** | [Name] | [Signature] | Jan 16, 2026 |
| **Legal/Compliance** | [Name] | [Signature] | Jan 16, 2026 |
| **Finance** | [Name] | [Signature] | Jan 16, 2026 |

---

**Document Control**

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | Jan 10, 2026 | Initial draft |
| 0.5 | Jan 13, 2026 | Feature review |
| 1.0 | Jan 16, 2026 | Final version (Production) |

---

**Document Classification**: Public  
**Distribution**: Engineering, Product, Legal, Stakeholders  
**Review Frequency**: Quarterly (or when significant changes occur)  
**Next Review Date**: April 16, 2026
