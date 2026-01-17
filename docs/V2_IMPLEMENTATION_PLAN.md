# WealthWise-AI: Version 1 Summary + Version 2 Implementation Plan

---

## PART A: WHAT WAS ACCOMPLISHED IN VERSION 1

### Overview
WealthWise-AI v1 is a **deterministic, rule-based income tax recommendation system** for Indian taxpayers. It focuses on correctness, auditability, and professional user experience without using embeddings or probabilistic AI for core logic.

### v1 Architecture

#### **Core Components**

1. **API Layer (FastAPI)**
   - Endpoint: `/tax/recommendation` → Returns ITR form, regime comparison, tax calculations
   - Endpoint: `/tax/chat` → Conversational Q&A about user's tax situation
   - Request validation via Pydantic schemas
   - Request logging middleware for auditability
   - Safety guardrails (domain checking, no-advice enforcement)

2. **Decision Engine (Rule-Based)**
   - **ITR Selector:** Determines which ITR form (1/2/3/4) user should file
     - ITR-1: Simple income (salary only)
     - ITR-2: Complex income (capital gains, multiple properties, unlisted equity, director status)
     - ITR-3: Business/profession income (non-presumptive)
     - ITR-4: Presumptive business income (44AD/44ADA)
   
   - **Missing Info Detector:** Identifies what data is still needed for accurate recommendations
   
   - **Regime Recommender:** Compares old vs new tax regime and recommends one

3. **Tax Computation Engine**
   - Deterministic calculation of:
     - Old regime tax (with slabs: 2.5L, 5L, 10L, 30%)
     - New regime tax (with slabs: 3L, 6L, 9L, 12L, 15L, 30%)
     - Taxable income calculation (gross income - deductions)
     - Income breakup (salary, interest, rental, capital gains, business)
   - No LLM involved in calculations

4. **Explanation Module**
   - Generates bullet-point explanations of why a regime is recommended
   - Uses LLM only to make explanations user-friendly (no logic changes)
   - Clear citation of rules from knowledge base

5. **Conversational Agent**
   - Handles follow-up questions from users
   - Routes queries to appropriate handlers
   - Uses conversation memory (last 5 turns)
   - Maintains context across chat

6. **Knowledge Base (RAG-Lite)**
   - Legal documents (Income Tax Act, Rules, Circulars)
   - ITR form instructions
   - Validation rules
   - NO vector embeddings (intentionally avoided for compliance)
   - Keyword-based search for regulatory references

7. **UI Layer (Streamlit)**
   - Form-based input for income/deductions/flags
   - Collapsible sections for organization
   - Dark theme (fintech-grade styling)
   - PDF download capability (professional report)
   - Chat interface for conversational guidance

### v1 Data Model (TaxProfile)

```python
TaxProfile:
  - profile_version
  - assessment_year
  - taxpayer
    - residential_status (resident/nri)
    - age_category (below_60/senior)
    - is_huf (yes/no)
  - income
    - salary (gross_salary, standard_deduction, exempt_allowances)
    - house_property (count, interest, net_income)
    - capital_gains (STCG/LTCG amounts)
    - other_sources (interest, dividends, pension, other)
    - business_profession (presumptive flag, net_profit)
  - deductions_old_regime
    - 80C, 80CCD(1B), 80D, 80TTA, 80G, other
  - taxes_paid
    - TDS, TCS, advance_tax, self_assessment_tax
  - flags
    - foreign_assets, director, unlisted_equity, agricultural_income
```

### v1 Features
✅ Deterministic ITR recommendation with clear reasons  
✅ Old vs New regime comparison with tax calculations  
✅ Income breakup transparency  
✅ Missing info detection  
✅ Conversational chat with context memory  
✅ PDF report generation (clean, no raw JSON)  
✅ Form 12BB generation | Backend | ✅ Done
✅ Audit logging for all requests  
✅ Safety guardrails (domain + language)  
✅ Professional Streamlit UI  
✅ Knowledge base with legal references  

### v1 Limitations
❌ Limited income/deduction fields (only ~30 out of 80+ needed)  
✅ ~~No document upload capability~~ **IMPLEMENTED in v2.0 with GPT-4 Vision**  
❌ No scenario analysis ("what-if" scenarios)  
❌ No investment breakdown (only total amounts)  
❌ No home loan details (only interest amount)  
❌ No rental income details (only net income)  
❌ No advanced deductions (80E, 80EE, 80EEA, 80GG, etc.)  
❌ Chat doesn't reference scenarios or detailed user data  
❌ UI doesn't progressively disclose fields based on user situation  

---

## PART B: VERSION 2 IMPLEMENTATION PLAN

### v2 Objectives
1. **Document-Assisted Inputs:** Users can upload Form 16 or bank statements
2. **Richer Data Capture:** TIER 1 + TIER 2 fields enable 85%+ of meaningful scenarios
3. **Scenario-Based Optimization:** "What-if" analysis showing tax savings
4. **Conversational Guidance:** Chat agents reference scenarios and user-specific data
5. **Progressive UI:** Fields appear based on user's situation, not all at once

### v2 Architecture (Agent-Based)

#### **Agent 1: Document Ingestion Agent** ✅ IMPLEMENTED
- **Input:** Uploaded PDF (Form 16, Bank Statement, Investment Statement, Home Loan Certificate, etc.)
- **Process:** Use GPT-4 Vision + PDF parsing to extract structured data
- **Output:** Partially extracted data with confidence flags
- **Characteristics:** All extraction marked as "user-verifiable"; users can override
- **Status:** ✅ **FULLY IMPLEMENTED** in v2.0
  - Universal document detector (20+ document types)
  - GPT-4 Vision extraction with OpenRouter
  - Field mapping to TaxFacts schema
  - Provenance tracking (source, confidence, timestamp)
  - Multi-document upload support
  - Extraction verification UI with edit capability

#### **Agent 2: TaxFacts Normalization Agent**
- **Input:** Data from multiple sources (UI, documents, chat clarifications)
- **Process:** 
  - Merge data from different sources
  - Resolve conflicts (e.g., if Form 16 says ₹15L but user entered ₹12L, flag it)
  - Validate against business rules
  - Track data provenance (source: "form16" | "manual" | "extracted" | "chat")
  - Add confidence scores (1.0 for user-entered, 0.6-0.8 for extracted)
- **Output:** Clean, canonical TaxFacts object (single source of truth)

#### **Agent 3: Scenario & Optimization Agent**
- **Input:** TaxFacts + User exploration preference
- **Process:**
  - Clone TaxFacts (immutable)
  - Modify one scenario variable (e.g., "increase 80C by ₹50k")
  - Recalculate tax using deterministic engine
  - Compare before/after
  - Rank scenarios by tax savings
- **Output:** List of scenarios with concrete savings numbers
- **Implementation:** Pure logic (no LLM here except for phrasing recommendations)

#### **Agent 4: Explanation & Chat Agent**
- **Input:** User question + TaxFacts + Scenario context
- **Process:**
  - Understand user intent (LLM)
  - Retrieve relevant deductions/scenarios from TaxFacts
  - Compose explanation grounded in user's actual data
  - Never expose raw JSON
  - Cite deduction sections (80C, 80E, etc.)
- **Output:** Natural language explanation
- **Examples:**
  - "Your gross salary is ₹15L. In the old regime, you'd pay ₹2.5L tax. If you increase 80C investments by ₹50k, you save ₹15,600."
  - "You have ₹2L rental income. You can claim depreciation of ₹20k and interest of ₹50k, reducing your taxable rental income to ₹1.3L."

### v2 Data Model: TaxFacts (Unified Internal Structure)

```python
class TaxFacts:
    # ===== TIER 1: MUST HAVE (Tax Calculation) =====
    
    # Taxpayer
    assessment_year: str
    residential_status: str  # resident | nri
    age_category: str  # below_60 | senior_60_80 | above_80
    huf_status: bool
    
    # Income - Salary
    salary_gross: float
    salary_standard_deduction_claim: bool
    salary_exempt_allowances: float
    
    # Income - House Property
    property_count: int
    property_letout_net_income: float
    
    # Income - Capital Gains
    capital_gains_stcg_111a: float
    capital_gains_stcg_other: float
    capital_gains_ltcg_112a: float
    capital_gains_ltcg_other: float
    
    # Income - Other Sources
    other_income_savings_interest: float
    other_income_fd_interest: float
    other_income_dividends: float
    other_income_family_pension: float
    other_income_other: float
    
    # Income - Business/Profession
    business_has_income: bool
    business_presumptive_opted: bool
    business_presumptive_section: str  # 44AD | 44ADA | null
    business_non_presumptive_profit: float
    
    # Deductions - Section 80
    deduction_80c: float
    deduction_80ccd_1b: float
    deduction_80d_self: float
    deduction_80g: float
    deduction_80tta: float
    deduction_other: float
    
    # Home Loan (TIER 1) - Canonical source for property deductions
    home_loan_interest_paid: float  # Use for Section 24 deduction
    home_loan_principal_paid: float
    
    # Taxes Paid
    taxes_tds: float
    taxes_advance_tax: float
    taxes_self_assessment_tax: float
    
    # ===== TIER 2: OPTIONAL (Scenario Enhancement) =====
    
    # Deductions - Advanced
    deduction_80d_spouse: float = 0
    deduction_80d_children: float = 0
    deduction_80d_parents: float = 0
    deduction_80e_education_loan_interest: float = 0
    deduction_80ee_home_loan_interest: float = 0
    deduction_80eea_home_loan_interest: float = 0
    deduction_80gg_house_rent: float = 0
    
    # Home Loan - Detailed
    home_loan_amount: float = 0
    home_loan_year_of_purchase: int = 0
    home_loan_first_time_buyer: bool = False
    
    # Investments - Breakdown
    investment_ppf_amount: float = 0
    investment_elss_amount: float = 0
    investment_lic_premium: float = 0
    investment_nps_amount: float = 0
    
    # Family
    spouse_name: str = ""
    spouse_pan: str = ""
    children_count: int = 0
    children_dob: List[str] = []
    
    # Losses
    loss_carryforward_amount: float = 0
    loss_carryforward_year: int = 0
    
    # Refunds
    previous_year_refund_status: str = ""  # pending | received | none
    previous_year_refund_amount: float = 0
    
    # ===== TIER 3: UI-ONLY (SEPARATE from TaxFacts) =====
    # NOTE: These fields are stored separately in UserIdentity schema,
    # NOT in TaxFacts. This keeps the tax computation core clean.
    # UserIdentity contains: name, PAN, DOB, email, phone, address,
    # gender, marital status, and investment account numbers.
    
    # ===== METADATA =====
    
    # Data Provenance
    source_mapping: Dict[str, str] = {}  # field_name -> "form16" | "manual" | "extracted" | "chat"
    confidence_mapping: Dict[str, float] = {}  # field_name -> 0.6-1.0
    extraction_timestamp: str = ""
    last_modified: str = ""
```

### v2 User Experience: Progressive Disclosure

#### **Stage 1: Essential (60 seconds)**
```
Welcome! Let's calculate your tax.

What's your gross salary?  [_________]
How much TDS was deducted?  [_________]
Assessment year?  [2025-26]

[GENERATE INITIAL RECOMMENDATION]
```

#### **Stage 2: Conditional Sections (2 minutes)**
```
Do you have a home loan?
  [Yes] → Show: Interest paid, Principal paid, Loan year
  [No]

Do you have investments (PPF, ELSS, LIC, NPS)?
  [Yes] → Show: PPF amount, ELSS amount, LIC premium, NPS
  [No]

Do you have rental income?
  [Yes] → Show: Net income, Gross rent, Repairs, Depreciation
  [No]

Do you have dependents (spouse, children)?
  [Yes] → Show: Spouse info, Children count
  [No]
```

#### **Stage 3: Scenarios (Optional, 1 minute)**
```
Based on your data, here are ways to save tax:

□ Increase 80C investments by ₹50k → Save ₹15,600
□ Claim house rent deduction (₹2L) → Save ₹60,000
□ Increase NPS by ₹50k → Save ₹15,600
□ Switch to new regime → Save ₹42,500

[CLICK ANY TO SEE IMPACT]
```

#### **Stage 4: Document Upload (Optional)**
```
Want to auto-fill? Upload Form 16 or Bank Statement
[UPLOAD AREA]

Extracted data (review & correct):
  Employer Name: [extracted] → Verify
  Gross Salary: [extracted] → Verify
  TDS Deducted: [extracted] → Verify
```

### v2 Scenario Definitions (8-10 High-Impact)

#### **Scenario 1: Increase Section 80C**
- **Action:** Increase 80C investments by ₹50,000
- **Calculation:** 
  - New 80C = (old 80C) + 50,000
  - New taxable income = gross income - (new deductions)
  - New tax = recalculate using tax slabs
  - Savings = old tax - new tax
- **Example Output:** "Increasing 80C investments by ₹50,000 saves you ₹15,600 in the old regime."

#### **Scenario 2: Claim House Rent Deduction (80GG)**
- **Condition:** Only if NOT claiming home loan interest; no HRA received; no owned house in city of employment
- **Action:** Claim ₹2,00,000 house rent deduction (if eligible)
- **Status:** POTENTIALLY ELIGIBLE — User must verify eligibility conditions
- **Calculation:** Same as above (if eligible)
- **Example Output:** "If eligible, claiming ₹2L house rent saves ₹60,000. Verify eligibility: (1) No HRA, (2) No owned house in employment city."

#### **Scenario 3: Claim Education Loan Interest (80E)**
- **Condition:** Only if user has education loan
- **Action:** Claim ₹1,00,000 education loan interest
- **Example Output:** "Claiming ₹1L education loan interest saves you ₹30,000."

#### **Scenario 4: Switch Tax Regime**
- **Action:** Compare old vs new regime (already done)
- **Output:** "Switching to new regime saves you ₹42,500."

#### **Scenario 5: Increase NPS Contribution**
- **Action:** Increase NPS by ₹50,000 (as 80CCD(1B) employee extra)
- **Calculation:** NPS within 80C cap (₹1.5L total) counts as 80C. Additional via 80CCD(1B) (₹50k extra) saves ₹15,600.
- **Example Output:** "Additional ₹50k NPS (via 80CCD(1B)) saves ₹15,600."
- **Note:** Employer NPS contribution (80CCD(2)) not modeled in v2; added in v3 if needed.

#### **Scenario 6: Claim Home Loan Interest (80EE)**
- **Condition:** Only if user has home loan + first-time buyer
- **Action:** Claim home loan interest deduction
- **Example Output:** "As a first-time buyer, claiming ₹1.5L home loan interest saves ₹45,000."

#### **Scenario 7: Add Medical Insurance for Parents (80D)**
- **Condition:** Only if user has parents
- **Action:** Add ₹25,000 medical insurance for parents
- **Example Output:** "Adding parent medical insurance (₹25k limit for seniors) saves you ₹7,500."
Standard Deduction on Rental Property (30%)**
- **Condition:** Only if user has let-out property with rental income
- **Action:** Claim 30% standard deduction on gross rental income (Section 24)
- **Calculation:** Deduction = 30% × gross rent. Tax savings = deduction × marginal rate
- **Example Output:** "On ₹2L gross rental income, claiming 30% standard deduction (₹60k) saves ₹18,000."
- **Note:** Separate from interest deduction on home loan; both can be claimed.
- **Example Output:** "Claiming ₹20k depreciation on rental property saves ₹6,000."

#### **Scenario 9: Carry Forward Loss**
- **Condition:** Only if user has loss carry-forward
- **Action:** Adjust taxable income by loss amount
- **Example Output:*Top 3 Best Single-Step Actions (Ranked by Savings)**
- **Action:** Show ranked list of top 3 applicable scenarios for this user
- **Ranking:** Sort all applicable scenarios by tax savings (highest first)
- **Example Output:** 
  1. "Switch to new regime → Save ₹42,500"
  2. "Claim house rent (₹2L, 80GG) → Save ₹60,000"
  3. "Increase 80C by ₹50k → Save ₹15,600"
- **Determinism:** Greedy ranking (no complex optimization); each scenario is independent and auditable.
- **Action:** Find best combination of deductions
- **Example Output:** "Your optimal deduction mix: ₹1.5L (80C) + ₹25k (80D) + ₹2L (80GG) saves ₹4.5L tax."

### v2 Implementation Checklist

#### **Day 1 (≈3 hours)**

- [ ] **1.1 Create TaxFacts Pydantic Schema** (1 hour)
  - File: `src/core/taxfacts.py` (NEW)
  - Include TIER 1 + TIER 2 + TIER 3 fields
  - Add data provenance tracking (source, confidence, timestamp)
  - Add validation rules (sanity checks on ranges)

- [ ] **1.2 Update TaxProfile Request Schema** (30 mins)
  - File: `src/api/schemas/request.py` (MODIFY)
  - Extend to match TaxFacts structure
  - Keep backward compatibility with v1 data

- [ ] **1.3 Create Normalization Agent** (45 mins)
  - File: `src/agent/normalization_agent.py` (NEW)
  - Implement conflict resolution logic
  - Implement data provenance tracking
  - Handle missing fields gracefully

- [ ] **1.4 Expand Streamlit UI - Progressive Disclosure** (45 mins)
  - File: `streamlit_app.py` (MODIFY)
  - Stage 1: Essential fields only (salary, TDS, year)
  - Stage 2: Conditional sections (if has home loan, investments, rental, dependents)
  - Stage 3: Scenario selection (checkboxes)
  - Stage 4: Document upload area ✅ **IMPLEMENTED** (multi-document upload with extraction verification)

- [ ] **1.5 Verify End-to-End** (30 mins)
  - Test that new TaxFacts flows through tax_engine.py
  - Verify old regime + new regime calculations still work
  - Ensure backward compatibility with v1

#### **Day 2 (≈5 hours)**

- [ ] **2.1 Build Scenario Engine** (1.5 hours)
  - File: `src/compute/scenario_engine.py` (NEW)
  - Implement clone-modify-recalculate pattern
  - Implement all 8-10 scenarios
  - Return before/after comparison with savings

- [ ] **2.2 Create Scenario Service** (1 hour)
  - File: `src/core/scenario_service.py` (NEW)
  - Determine which scenarios are applicable to user
  - Rank scenarios by savings potential
  - Format scenarios for UI/chat presentation

- [ ] **2.3 Enhance Chat Agent** (1 hour)
  - File: `src/agent/router.py` (MODIFY)
  - Add scenario-aware responses
  - Reference user's actual data in responses
  - Suggest relevant scenarios based on user's situation

- [ ] **2.4 Add Document Upload UI** (1 hour)
  - File: `streamlit_app.py` (MODIFY)
  - Add file uploader widget
  - Create placeholder extraction display
  - Mark all extracted data as "verified from Form 16 - please review"
  - Ready for real parsing in v2.1

- [ ] **2.5 UI Polish + Testing** (1.5 hours)
  - Test progressive disclosure logic
  - Test scenario calculations
  - Test chat with scenarios
  - Update Streamlit styling
  - Create sample data for testing

### v2 New/Modified Files

#### **NEW Files:**
```
src/core/taxfacts.py                    ← TaxFacts Pydantic schema
src/agent/normalization_agent.py        ← Data normalization + conflict resolution
src/compute/scenario_engine.py          ← Scenario cloning + recalculation
src/core/scenario_service.py            ← Scenario ranking + presentation
src/api/schemas/taxfacts_response.py    ← Response schema for scenarios
```

#### **MODIFIED Files:**
```
src/api/schemas/request.py              ← Extend TaxProfile to match TaxFacts
src/api/app.py                          ← Add /tax/scenarios endpoint
src/core/recommendation_service.py      ← Call TaxFacts normalization first
src/compute/tax_engine.py               ← Accept TaxFacts instead of dict
src/agent/router.py                     ← Add scenario-aware responses
streamlit_app.py                        ← Progressive disclosure + scenarios + upload
```

#### **UNCHANGED:**
```
src/decision/itr_selector.py            ← Still used by tax engine
src/decision/missing_info_detector.py   ← Still used by recommendation service
src/explain/explain_regime_choice.py    ← Still used
src/safety/guardrails.py                ← Still used
src/core/audit_logger.py                ← Still used
src/conversation/memory.py              ← Still used
src/llm/llm_adapter.py                  ← Still used
src/retrieval/basic_retriever.py        ← Still used (for citations)
```

### v2 Key Implementation Details

#### **TaxFacts vs UserIdentity Separation:**
- **TaxFacts:** Contains only fields that impact tax calculation (TIER 1 + TIER 2)
  - Single source of truth for deterministic logic
  - No personal identity info
  - Fully auditable

- **UserIdentity:** Separate schema for UI-only fields (TIER 3)
  - Stores: name, PAN, DOB, email, phone, address, gender, marital status
  - Stores: investment account numbers, policy numbers, scheme names
  - Optional; not used in tax calculations
  - Improves UX without cluttering tax logic

#### **Backward Compatibility:**
- v1 API endpoints still work
- v1 data format still accepted
- v2 extends, doesn't replace

#### **Data Flow (v2):**
```
User Input (UI form + uploaded doc)
         ↓
Document Ingestion Agent (extract if doc provided)
         ↓
TaxFacts Normalization Agent (merge, validate, provenance)
         ↓
Deterministic Tax Engine (calculate TIER 1 results)
         ↓
Scenario Engine (clone + recalculate for each scenario)
         ↓
Response: Recommendation + Scenarios + Data Provenance
```

#### **Determinism Guarantee:**
- All tax calculations come from `tax_engine.py` (unchanged logic)
- All scenarios use same engine (cloned data only)
- LLM never touches numbers
- LLM only phrases results

#### **Confidence & Provenance:**
```python
# Example output showing provenance:
{
    "salary_gross": 1500000,
    "salary_source": "form16",
    "salary_confidence": 0.99,
    
    "deduction_80c": 150000,
    "deduction_80c_source": "manual",
    "deduction_80c_confidence": 1.0,
    
    "home_loan_interest": 100000,
    "home_loan_interest_source": "extracted",
    "home_loan_interest_confidence": 0.75,
}
```

---

## PART C: COMPARISON SUMMARY

| Aspect | v1 | v2 |
|--------|----|----|
| **ITR Recommendation** | ✅ Deterministic | ✅ Same |
| **Tax Calculation** | ✅ Deterministic | ✅ Same |
| **Regime Comparison** | ✅ Yes | ✅ Enhanced |
| **Income/Deduction Fields** | ~30 | ~50-60 (TIER 1+2) |
| **Home Loan** | ✅ Interest only | ✅ Full details |
| **Deductions** | 5 sections | 9+ sections |
| **Scenarios** | ❌ None | ✅ 8-10 scenarios |
| **Document Upload** | ❌ None | ✅ **IMPLEMENTED** (GPT-4 Vision extraction) |
| **Progressive UI** | ❌ All fields | ✅ Conditional |
| **Data Provenance** | ❌ None | ✅ Full tracking |
| **Scenario Chat** | ❌ Generic | ✅ User-specific |
| **Confidence Flags** | ❌ None | ✅ On extraction |
| **Development Time** | ~40 hrs (v1) | ~8 hrs (v2) |

---

## PART D: v2 Success Criteria

✅ Users can enter 50+ TIER 1+2 fields (progressive disclosure)  
✅ Scenarios show real tax savings (cloned + recalculated)  
✅ Chat references user-specific data  
✅ **Document upload IMPLEMENTED with GPT-4 Vision extraction (20+ document types)**  
✅ All recommendations remain deterministic and auditable  
✅ Data provenance tracked (source + confidence)  
✅ v1 API compatibility maintained  
✅ Streamlit UI with finance-grade dark theme design system  
✅ **Universal document extraction pipeline operational**  
✅ **Multi-document upload with confidence scoring**  
✅ **Extraction verification UI with edit capability**  

---
