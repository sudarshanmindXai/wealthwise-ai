# WealthWise AI - Data & RAG Requirements

> **Purpose**: Lists all documents, datasets, and assets required to build the product

---

## 1. RAG Knowledge Base Documents

### Tier 1: Core Legal Documents (High Priority)

| Document | Source | Format | Usage |
|----------|--------|--------|-------|
| **Income Tax Act, 1961** | incometaxindia.gov.in | PDF/MD | Guardian citations |
| **Income Tax Rules, 1962** | incometaxindia.gov.in | PDF/MD | Rule 3 (Perquisites), etc. |
| **Finance Act 2025** | indiabudget.gov.in | PDF/MD | Budget 2025 amendments |
| **CBDT Circulars (FY 25-26)** | incometaxindia.gov.in | PDF | Latest clarifications |

**Key Sections to Ingest**:
| Section | Description | Guardian |
|---------|-------------|----------|
| Sec 10 | Exempt Income (HRA, LTA) | Salary Sentinel |
| Sec 24 | House Property Deduction | Windfall Warden |
| Sec 44ADA | Presumptive Professionals | Hustle Shield |
| Sec 80C/80CCD/80D | Chapter VI-A Deductions | Salary Sentinel |
| Sec 87A | Rebate for Low Income | Math Engine |
| Sec 111A/112A | Capital Gains | Portfolio Architect |
| Sec 115BAC | New Tax Regime | Math Engine |
| Sec 115BBH | Crypto/VDA Taxation | Portfolio Architect |
| Sec 64(2) | Clubbing Provisions | Windfall Warden |
| Rule 3 | Perquisite Valuation | Salary Sentinel |

### Tier 2: Supplementary Documents (Medium Priority)

| Document | Purpose |
|----------|---------|
| ITR Form Instructions (ITR-1, ITR-2, ITR-3) | Form field mapping |
| Form 16 Format Specifications | OCR extraction guide |
| Form 12BB Template | Output generation reference |
| CAS Statement Format | Investment data parsing |

### Tier 3: Reference Documents (Low Priority)

| Document | Purpose |
|----------|---------|
| SEBI Circulars | Buyback rules |
| GST Thresholds | Audit trigger reference |
| PF/Gratuity Rules | Exemption calculations |

---

## 2. Synthetic Test Data

### Primary Persona: "Rohan Sharma"

**Profile**: Salaried + Freelancer + Investor (The Modern Moonlighter)

```json
{
  "name": "Rohan Sharma",
  "pan": "ABCRS1234P",
  "fy": "2025-26",
  "age": 32,
  "city": "Bangalore",
  "income": {
    "salary": {
      "employer": "TechCorp India Pvt Ltd",
      "gross": 1800000,
      "basic": 900000,
      "da": 0,
      "hra_received": 300000,
      "special_allowance": 450000,
      "lta": 50000,
      "employer_nps": 0,
      "tds": 180000
    },
    "freelance": {
      "platform": "Upwork/Fiverr",
      "gross_receipts": 600000,
      "actual_expenses": 150000,
      "profession": "technical_consultancy"
    },
    "investments": {
      "ltcg_equity": 80000,
      "stcg_equity": 0,
      "dividends": 25000,
      "crypto_gains": 50000,
      "crypto_losses": 20000
    }
  },
  "deductions": {
    "section_80c": 150000,
    "section_80d": 25000,
    "section_80ccd_1b": 0
  },
  "rent_paid_annual": 240000,
  "home_loan": null
}
```

### Secondary Personas

| Persona | Profile | Tests |
|---------|---------|-------|
| **Priya Mehta** | Crypto Trader | 115BBH no set-off |
| **Vikram Singh** | UHNI (₹6Cr) | Surcharge arbitrage |
| **Anita Rao** | Landlord with HUF | Clubbing (Sec 64) |
| **Karan Dev** | F&O Trader | Audit triggers |
| **Sneha Patel** | Senior Citizen | Different slabs |

---

## 3. Sample Documents (for OCR Testing)

| Document Type | Samples Needed | Purpose |
|---------------|----------------|---------|
| Form 16 Part A/B | 5 variations | Salary extraction |
| Bank Statement PDF | 3 formats (HDFC, ICICI, SBI) | Freelance credits |
| Bank Statement CSV | 3 formats | Parser testing |
| CAS Statement (CAMS/Karvy) | 2 samples | Investment holdings |
| Broker P&L Statement | 2 formats (Zerodha, Groww) | Capital gains |
| Rent Receipts | 3 samples | HRA validation |

---

## 4. Glossary Data (glossary.json)

**Location**: `backend/data/glossary.json`

```json
{
  "terms": {
    "87A": {
      "full_name": "Section 87A Rebate",
      "user_friendly": "Zero Tax Rebate",
      "description": "Full tax rebate if income ≤ ₹12L (New) or ₹5L (Old)",
      "applicable_guardian": "math_engine"
    },
    "44ADA": {
      "full_name": "Section 44ADA Presumptive Taxation",
      "user_friendly": "Presumptive Shield",
      "description": "50% flat profit for professionals < ₹75L receipts",
      "applicable_guardian": "hustle_shield"
    },
    "115BBH": {
      "full_name": "Section 115BBH VDA Taxation",
      "user_friendly": "Crypto Trap",
      "description": "Flat 30% tax, no set-off allowed",
      "applicable_guardian": "portfolio_architect"
    }
  }
}
```

---

## 5. Reference Data Files

### Tax Constants (constants.py)

Already defined in `TAX_RULES_CONSTANTS.md` - must be mirrored to:
- `backend/app/engine/constants.py`

### Metro Cities (for HRA)

```python
METRO_CITIES = ["Delhi", "Mumbai", "Chennai", "Kolkata"]
```

### Eligible Professions (44ADA)

```python
ELIGIBLE_44ADA_PROFESSIONS = [
    "legal",
    "medical", 
    "engineering",
    "architecture",
    "accountancy",
    "technical_consultancy",
    "interior_decoration",
    "film_artist",
    "company_secretary",
    "authorized_representative"
]
```

---

## 6. Vector Database Schema (ChromaDB)

### Collections

| Collection | Content | Chunking |
|------------|---------|----------|
| `income_tax_act` | IT Act sections | By section |
| `it_rules` | IT Rules | By rule |
| `cbdt_circulars` | CBDT circulars | By paragraph |
| `glossary` | Tax terms | By term |

### Metadata Fields

```python
{
    "section_number": "87A",
    "chapter": "VIII",
    "act": "Income Tax Act 1961",
    "last_amended": "Finance Act 2025",
    "guardian_relevance": ["salary_sentinel", "math_engine"]
}
```

---

## 7. File Checklist

### Must Have (Phase 1)
- [ ] Income Tax Act sections (10, 24, 44ADA, 80C-80D, 87A, 111A-112A, 115BAC, 115BBH)
- [ ] Rule 3 (Perquisites)
- [ ] Rohan synthetic dataset (JSON + CSV)
- [ ] 3 sample Form 16 PDFs
- [ ] glossary.json

### Should Have (Phase 2)
- [ ] 3 sample bank statements
- [ ] CAS statement samples
- [ ] Secondary persona datasets
- [ ] CBDT circulars FY 25-26

### Nice to Have (Phase 3)
- [ ] ITR form instructions
- [ ] Historical amendments reference
- [ ] State-specific rules (if any)
