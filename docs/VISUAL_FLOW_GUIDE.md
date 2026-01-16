# Document Upload Flow - Visual Guide

## User Journey: From Upload to Tax Calculation

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STAGE 1: ENTER BASIC INCOME DETAILS                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Assessment Year: 2024-25                                    │  │
│  │ • Residential Status: Resident India                          │  │
│  │ • Annual Salary: ₹ 15,00,000                                 │  │
│  │ • TDS Paid: ₹ 1,50,000                                       │  │
│  │ • Age: 30                                                     │  │
│  │                                                               │  │
│  │  [Get Tax Summary] ← Click this first                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STAGE 1.5: UPLOAD DOCUMENTS (OPTIONAL)                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 📄 Upload Documents (Optional)                                │  │
│  │                                                               │  │
│  │ Upload tax documents for automatic data extraction.          │  │
│  │ Supported: Form 16, Bank Statements, Home Loan Certificates  │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────┐     │  │
│  │  │  Drag and drop PDFs here or click to browse        │     │  │
│  │  │                                                     │     │  │
│  │  │           [Choose PDF files]                        │     │  │
│  │  └─────────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  PROCESSING: AUTO-DETECTION & EXTRACTION                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 🔍 Analyzing form_16.pdf...                                   │  │
│  │                                                               │  │
│  │  Step 1/3: Detecting document type... ✓                      │  │
│  │  Step 2/3: Extracting data with GPT-4 Vision... ⏳           │  │
│  │  Step 3/3: Mapping to tax fields... ⏳                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  VERIFICATION: REVIEW EXTRACTED DATA                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ✅ Extracted data from form_16.pdf                            │  │
│  │    (Type: form_16, Confidence: 95%)                          │  │
│  │                                                               │  │
│  │  ▼ 📋 form_16.pdf (form_16)                                  │  │
│  │    ┌────────────────────────────────────────────────────┐    │  │
│  │    │ GROSS SALARY                                       │    │  │
│  │    │ ₹1,500,000                                        │    │  │
│  │    │ Source: form_16.pdf | Confidence: 95% 🟢          │    │  │
│  │    ├────────────────────────────────────────────────────┤    │  │
│  │    │ TDS DEDUCTED                                       │    │  │
│  │    │ ₹150,000                                          │    │  │
│  │    │ Source: form_16.pdf | Confidence: 90% 🟢          │    │  │
│  │    ├────────────────────────────────────────────────────┤    │  │
│  │    │ FINANCIAL YEAR                                     │    │  │
│  │    │ 2024-25                                            │    │  │
│  │    │ Source: form_16.pdf | Confidence: 100% 🟢         │    │  │
│  │    ├────────────────────────────────────────────────────┤    │  │
│  │    │ EMPLOYER NAME                                      │    │  │
│  │    │ ABC Corporation                                    │    │  │
│  │    │ Source: form_16.pdf | Confidence: 95% 🟢          │    │  │
│  │    └────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │    [Apply to Form] ← Click to auto-populate                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  AUTO-POPULATION: FORM FIELDS UPDATED                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ✅ Data applied to form! Review and adjust as needed.        │  │
│  │                                                               │  │
│  │  STAGE 1: INCOME DETAILS (Updated)                           │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │ Annual Salary: ₹ 1,500,000 ← From form_16.pdf         │  │  │
│  │  │ TDS Paid: ₹ 150,000 ← From form_16.pdf                │  │  │
│  │  │ Assessment Year: 2024-25 ← From form_16.pdf           │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                               │  │
│  │  User can now review and edit if needed...                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STAGE 2: DEDUCTIONS & ASSETS                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ User can continue with deductions...                          │  │
│  │ • Home Loan Interest                                          │  │
│  │ • 80C Investments                                             │  │
│  │ • Medical Insurance (80D)                                     │  │
│  │ • etc.                                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  FINAL RESULT: TAX CALCULATION                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 💰 TAX SUMMARY                                                │  │
│  │                                                               │  │
│  │  Recommended Regime: NEW REGIME                              │  │
│  │                                                               │  │
│  │  Old Regime Tax: ₹2,34,000                                   │  │
│  │  New Regime Tax: ₹1,95,000                                   │  │
│  │  You Save: ₹39,000 🎉                                        │  │
│  │                                                               │  │
│  │  Data Sources:                                                │  │
│  │  • Salary: form_16.pdf (95% confidence)                      │  │
│  │  • TDS: form_16.pdf (90% confidence)                         │  │
│  │  • Deductions: User entered                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Behind the Scenes: Technical Flow

```
USER ACTION                    SYSTEM PROCESSING                    RESULT
──────────────────────────────────────────────────────────────────────────

[Upload PDF]
    │
    └─→ Save to temp file
            │
            ├─→ Extract text (PyPDF2)
            │       │
            │       └─→ Send to GPT-4 Turbo
            │               │
            │               └─→ "This is a Form 16"
            │                      Confidence: 95%
            │
            ├─→ Select extraction prompt
            │       │
            │       └─→ "Extract: gross_salary, 
            │              tds_deducted, ..."
            │
            ├─→ Send PDF to GPT-4 Vision
            │       │
            │       └─→ Returns JSON:
            │              {
            │                "gross_salary": 1500000,
            │                "tds_deducted": 150000,
            │                ...
            │              }
            │
            ├─→ Map to TaxFacts schema
            │       │
            │       └─→ {
            │              "salary_gross": 1500000,
            │              "taxes_tds": 150000
            │           }
            │
            ├─→ Add provenance
            │       │
            │       └─→ {
            │              "source": "form_16.pdf",
            │              "confidence": 0.95,
            │              "timestamp": "2025-01-15T10:30:00"
            │           }
            │
            └─→ Delete temp file
                    │
                    └─→ Display to user ──────────→ ✅ Ready to verify


[Click "Apply to Form"]
    │
    └─→ Update session state
            │
            └─→ Populate form fields
                    │
                    └─→ st.rerun() ──────────→ ✅ Form auto-filled


[Click "Get Tax Summary"]
    │
    └─→ Build TaxProfile
            │
            ├─→ Include extracted data
            │       (with provenance)
            │
            └─→ Send to Tax Engine
                    │
                    ├─→ Calculate Old Regime
                    ├─→ Calculate New Regime
                    └─→ Compare & Recommend ──→ ✅ Tax summary shown
```

---

## Error Handling Flow

```
SCENARIO 1: Unknown Document Type
────────────────────────────────────
[Upload unknown.pdf]
    │
    └─→ Extract text
            │
            └─→ GPT-4: "Cannot determine type"
                    │
                    └─→ Display warning ──→ ⚠️ "Could not identify document type"
                            │
                            └─→ User can re-upload or enter manually


SCENARIO 2: Low Confidence Extraction
──────────────────────────────────────
[Upload poor_quality_scan.pdf]
    │
    └─→ Extract text (blurry/unclear)
            │
            └─→ GPT-4 Vision: Returns data with low confidence
                    │
                    └─→ Display with red indicators ──→ 🔴 Confidence: 45%
                            │
                            └─→ User verifies against original document


SCENARIO 3: Extraction Timeout
───────────────────────────────
[Upload large_file.pdf]
    │
    └─→ Processing...
            │
            └─→ GPT-4 Vision (30 seconds timeout)
                    │
                    └─→ Timeout error ──→ ❌ "Processing timed out"
                            │
                            └─→ User can retry or enter manually


SCENARIO 4: API Key Invalid
────────────────────────────
[Upload any PDF]
    │
    └─→ Call OpenRouter
            │
            └─→ 401 Unauthorized ──→ ❌ "API key invalid"
                    │
                    └─→ Check configuration
```

---

## Multi-Document Flow

```
USER UPLOADS MULTIPLE DOCUMENTS
────────────────────────────────

[Upload 3 files: form_16.pdf, bank_statement.pdf, home_loan.pdf]
    │
    ├─→ Process form_16.pdf
    │       ├─→ Detect: "form_16" (95% confidence)
    │       ├─→ Extract: gross_salary, tds
    │       └─→ Store: session_state["extracted_data"]["form_16_abc"]
    │
    ├─→ Process bank_statement.pdf
    │       ├─→ Detect: "bank_statement" (90% confidence)
    │       ├─→ Extract: interest_income
    │       └─→ Store: session_state["extracted_data"]["bank_statement_xyz"]
    │
    └─→ Process home_loan.pdf
            ├─→ Detect: "home_loan_certificate" (95% confidence)
            ├─→ Extract: interest_paid, principal_paid
            └─→ Store: session_state["extracted_data"]["home_loan_def"]

Display all extracted data:
─────────────────────────────
📋 form_16.pdf (form_16)
   • Gross Salary: ₹1,500,000 (95% 🟢)
   • TDS: ₹150,000 (90% 🟢)

📋 bank_statement.pdf (bank_statement)
   • Interest Income: ₹25,000 (85% 🟢)

📋 home_loan.pdf (home_loan_certificate)
   • Interest Paid: ₹200,000 (95% 🟢)
   • Principal Paid: ₹150,000 (95% 🟢)

[Apply All to Form] ← One click to populate all fields
```

---

## Confidence Scoring System

```
CONFIDENCE LEVELS
─────────────────

🟢 HIGH (>80%)
   • Standard Form 16 from payroll software
   • Bank statements from major banks
   • Computer-generated certificates
   → Use with minimal verification

🟡 MEDIUM (50-80%)
   • Non-standard formats
   • Partially handwritten documents
   • Low-resolution scans
   → Verify key numbers against original

🔴 LOW (<50%)
   • Handwritten receipts
   • Poor quality scans
   • Unclear/smudged text
   → Verify all fields carefully or re-upload


CONFIDENCE CALCULATION
──────────────────────

Overall Document Confidence = Average of:
1. Text clarity (PyPDF2 extraction quality)
2. Field completeness (all required fields found?)
3. Format match (matches expected template?)
4. LLM confidence (GPT-4 certainty in extraction)

Per-Field Confidence = Based on:
1. Text clarity in that field's location
2. Format validation (PAN format correct?)
3. Numeric reasonability (salary > 0?)
4. LLM certainty for that specific field
```

---

## Data Provenance Tracking

```
EVERY EXTRACTED FIELD HAS METADATA
───────────────────────────────────

Field: salary_gross
Value: 1500000
Provenance:
  ├─ source: "form_16.pdf"
  ├─ source_type: "document_extraction"
  ├─ confidence: 0.95
  ├─ extraction_timestamp: "2025-01-15T10:30:00Z"
  ├─ llm_model: "openai/gpt-4-vision-preview"
  ├─ original_text: "Gross Salary: Rs. 15,00,000"
  └─ verified_by_user: false


When user clicks "Apply to Form":
  └─ verified_by_user: true


For tax calculation:
  └─ Tax Summary shows:
      "Salary: ₹15,00,000 (Source: form_16.pdf, 95% confidence)"


For audit trail:
  └─ All calculations traceable back to source document
```

---

## Design System in Action

```
WEALTHWISE DARK THEME
─────────────────────

┌────────────────────────────────────────────────────────────┐
│ TAX INTELLIGENCE PLATFORM                    [Vault Navy]  │ ← Header
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │ 📄 Upload Documents                [Slate Glass] │     │ ← Card
│  │                                                   │     │
│  │  Upload tax documents for automatic extraction   │     │
│  │  [Audit Grey text]                                │     │
│  │                                                   │     │
│  │  ┌────────────────────────────────────────────┐  │     │
│  │  │ Choose PDF files [Slate Glass background] │  │     │ ← Input
│  │  └────────────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │ 📋 form_16.pdf (form_16)           [Slate Glass] │     │
│  │                                                   │     │
│  │  GROSS SALARY                                     │     │
│  │  ₹1,500,000 [JetBrains Mono, Ledger White]      │     │ ← Number
│  │  Source: form_16.pdf | Confidence: 95% 🟢        │     │ ← Provenance
│  │  [Audit Grey]                                     │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  [Apply to Form] ← Net-Gain Green button                  │ ← Action
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │ 💰 TAX SUMMARY                     [Slate Glass] │     │
│  │                                                   │     │
│  │  You Save: ₹39,000 [JetBrains Mono, Green]      │     │ ← Savings
│  │  Tax Liability: ₹1,95,000 [JetBrains Mono, Red] │     │ ← Liability
│  └──────────────────────────────────────────────────┘     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

**Visual guide complete. Ready for user testing!**
