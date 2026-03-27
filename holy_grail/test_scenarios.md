# WealthWise AI - Test Scenarios
> **Context**: FY 2025-26 (AY 2026-27)  
> **Purpose**: Validation constraints for the Math Engine

---

## Validation Rules

> [!IMPORTANT]
> Run these scenarios against `engine/calculator.py`. If output diverges by **more than ₹10**, the build fails.

---

## 1. The "Zero Tax" Cliff (Section 87A Marginal Relief)

*Validates: New Regime Rebate Logic & Cliff Smoothing*

### Scenario A: The "Safe Zone"

| Field | Value |
|-------|-------|
| Input | Net Taxable Income = ₹12,00,000 |
| Logic | Income ≤ ₹12L → Rebate applies |
| **Expected Tax** | **₹0** |

### Scenario B: The "Cliff Edge" (Marginal Relief)

| Field | Value |
|-------|-------|
| Input | Net Taxable Income = ₹12,10,000 |
| Base Tax Calc | (12.1L-12L)×15% + (12L-8L)×10% + (8L-4L)×5% = ₹1,500 + ₹40,000 + ₹20,000 = ₹61,500 |
| Excess Income | ₹12,10,000 - ₹12,00,000 = **₹10,000** |
| Relief Rule | Tax ≯ Excess Income |
| **Expected Tax** | **₹10,000** (+ 4% Cess = ₹10,400) |

### Scenario C: The "No Relief" Zone

| Field | Value |
|-------|-------|
| Input | Net Taxable Income = ₹12,80,000 |
| Logic | Excess (₹80k) > Base Tax (≈₹72k). Relief not applicable |
| **Expected Tax** | **₹72,000** (+ Cess) |

---

## 2. The Portfolio Architect (Capital Gains)

*Validates: Section 112A, 115BBH, Set-off Rules*

### Scenario D: The "Harvesting" Check

| Field | Value |
|-------|-------|
| LTCG (Equity) | ₹1,40,000 |
| STCG (Equity) | ₹50,000 |
| LTCG Tax | (₹1,40,000 - ₹1,25,000) × 12.5% = **₹1,875** |
| STCG Tax | ₹50,000 × 20% = **₹10,000** |
| **Expected Tax** | **₹11,875** (+ Cess) |

### Scenario E: The "Crypto Trap" (No Set-off)

| Field | Value |
|-------|-------|
| Salary Income | ₹15,00,000 |
| Crypto Loss | (₹2,00,000) |
| Crypto Gain | ₹1,00,000 |
| Salary Tax | Calculated on ₹15L independently |
| Crypto Tax | 30% × ₹1,00,000 = **₹30,000** (loss IGNORED) |
| **Critical Check** | Taxable Income NOT reduced by ₹1L net loss |
| **Expected Tax** | (Salary Tax) + ₹30,000 + Cess |

---

## 3. The Hustle Shield (Presumptive 44ADA)

*Validates: Business Income Computation*

### Scenario F: The "Moonlighter"

| Field | Value |
|-------|-------|
| Salary | ₹20,00,000 |
| Freelance Receipts | ₹10,00,000 |
| Presumptive Profit | 50% × ₹10L = **₹5,00,000** |
| Total Taxable | ₹25,00,000 |
| **Expected Tax** | Slab calc on ₹25,00,000 |

### Scenario G: The "Limit Breach"

| Field | Value |
|-------|-------|
| Freelance Receipts | ₹80,00,000 |
| Logic | Receipts > ₹75L (Enhanced Limit) |
| Action | 44ADA **NOT Applicable** |
| **Output Flag** | `REQUIRES_AUDIT = True` |

---

## 4. The Windfall Warden (HUF & Rent)

*Validates: Clubbing & Section 24*

### Scenario H: The "Clubbing" Preventer

| Field | Value |
|-------|-------|
| HUF Fund Source | "Transfer from Personal Savings" |
| HUF Income | ₹5,00,000 |
| Logic | Sec 64(2) - Self-acquired property without consideration |
| **Action** | Add ₹5L back to Individual's Taxable Income |
| **Output** | HUF Tax = 0; Individual Tax increases |

### Scenario I: The "Rent Standard Deduction"

| Field | Value |
|-------|-------|
| Rent Received | ₹6,00,000 |
| NAV | ₹6,00,000 |
| Standard Deduction (Sec 24) | 30% × NAV = **₹1,80,000** |
| Taxable HP Income | **₹4,20,000** (not ₹6L) |

---

## 5. The Regime Showdown (Optimization)

*Validates: Old vs New Comparison*

### Scenario J: The "Rent Heavy" User

| Field | Value |
|-------|-------|
| Gross Salary | ₹15,00,000 |
| Rent Paid | ₹3,00,000 (Metro) |
| 80C Investments | ₹1,50,000 |

**New Regime Calculation**:
- Taxable: ₹15L - ₹75k = ₹14.25L
- Tax: ≈ ₹1.35L

**Old Regime Calculation**:
- HRA Exemption: Min(Actual, 50% Basic, Rent-10% Basic) ≈ ₹2.5L
- Net Taxable: ₹15L - ₹50k - ₹1.5L - ₹2.5L = ₹10.5L
- Tax: ≈ ₹1.25L

| **Output** | "Recommend Old Regime" (Savings ≈ ₹10k) |

---

## 6. Guardian Integration Tests

### Salary Sentinel Tests

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| SS-01 | NPS under-utilized | 80CCD(2): ₹0, Basic: ₹10L | "Add ₹1.4L NPS employer" |
| SS-02 | EV opportunity | Slab 30%, Car EMI: ₹30K | "Recommend EV Lease" |
| SS-03 | HRA claim possible | Rent: ₹25K/mo, HRA claimed: ₹0 | "Claim HRA exemption" |

### Portfolio Architect Tests

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| PA-01 | Loss harvesting | Unrealized LTCG: ₹1L, YTD: ₹0 | "Book ₹1L tax-free" |
| PA-02 | Buyback warning | Slab: 30%, Buyback offer | "Sell on market" |
| PA-03 | Crypto isolation | Crypto loss: ₹50K | "Cannot offset" |

### Hustle Shield Tests

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| HS-01 | 44ADA eligible | Receipts: ₹50L, Expenses: 60% | "Use 44ADA" |
| HS-02 | Over limit | Receipts: ₹80L | "44ADA not allowed" |

### Windfall Warden Tests

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| WW-01 | Rent optimization | Rent: ₹5L | "Claim 30% deduction" |
| WW-02 | Gift taxable | Gift: ₹1L, From: Friend | "₹1L taxable" |
| WW-03 | Gift exempt | Gift: ₹1L, From: Parent | "Exempt" |

---

## 7. Test Data: Rohan Profile

```json
{
  "name": "Rohan Sharma",
  "pan": "ABCRS1234P",
  "fy": "2025-26",
  "income": {
    "salary": {
      "gross": 1800000,
      "basic": 900000,
      "hra_received": 300000,
      "tds": 180000
    },
    "freelance": {
      "receipts": 600000,
      "expenses": 150000
    },
    "investments": {
      "ltcg_realized": 80000,
      "stcg_realized": 0
    }
  },
  "deductions_claimed": {
    "80c": 150000,
    "80d": 25000
  },
  "rent_paid_annual": 240000,
  "city": "Bangalore"
}
```

---

## 8. Test Commands

```bash
# Run all math engine tests
pytest tests/unit/math_engine/ -v

# Run with ₹10 tolerance check
pytest -k "marginal_relief" --tolerance=10

# Run guardian tests
pytest tests/unit/guardians/ -v

# Run full validation suite
pytest tests/ --cov=app --cov-report=html
```