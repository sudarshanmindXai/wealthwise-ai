# WealthWise AI - Tax Rules & Constants
> **Assessment Year**: 2026-27 (FY 2025-26)  
> **Last Updated**: January 2026  
> **Source**: Union Budget 2025 (Enacted)

---

## ⚠️ Important Notice

> [!CAUTION]
> These constants are based on **Union Budget 2025**. Any changes in future budgets apply to the next Financial Year.

---

## 1. Income Tax Slabs

### New Regime (Default) - Section 115BAC(1A)

> [!IMPORTANT]
> **Budget 2025 Updated Slabs** - These are the official enacted slabs.

| Income Range (₹) | Tax Rate |
|-----------------|----------|
| 0 - 4,00,000 | **NIL** |
| 4,00,001 - 8,00,000 | **5%** |
| 8,00,001 - 12,00,000 | **10%** |
| 12,00,001 - 16,00,000 | **15%** |
| 16,00,001 - 20,00,000 | **20%** |
| 20,00,001 - 24,00,000 | **25%** |
| Above 24,00,000 | **30%** |

```python
NEW_REGIME_SLABS = [
    (400000, 0.00),    # 0-4L: NIL
    (800000, 0.05),    # 4-8L: 5%
    (1200000, 0.10),   # 8-12L: 10%
    (1600000, 0.15),   # 12-16L: 15%
    (2000000, 0.20),   # 16-20L: 20%
    (2400000, 0.25),   # 20-24L: 25%
    (float('inf'), 0.30),  # Above 24L: 30%
]

STANDARD_DEDUCTION_NEW = 75000
```

### Old Regime (Optional)

| Income Range (₹) | Tax Rate |
|-----------------|----------|
| 0 - 2,50,000 | NIL |
| 2,50,001 - 5,00,000 | 5% |
| 5,00,001 - 10,00,000 | 20% |
| Above 10,00,000 | 30% |

```python
OLD_REGIME_SLABS = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
    (float('inf'), 0.30),
]

STANDARD_DEDUCTION_OLD = 50000
```

---

## 2. Rebate under Section 87A

| Regime | Threshold | Max Rebate |
|--------|-----------|------------|
| New Regime | ₹12,00,000 | 100% waiver (up to ₹60,000) |
| Old Regime | ₹5,00,000 | 100% waiver (up to ₹12,500) |

**Marginal Relief** (New Regime): Tax Payable cannot exceed income exceeding ₹12L.

```python
REBATE_87A = {
    "new": {
        "threshold": 1200000,
        "max_rebate": 60000,
    },
    "old": {
        "threshold": 500000,
        "max_rebate": 12500,
    }
}

# Marginal Relief applicable for income between 12L-12.75L
MARGINAL_RELIEF_CEILING = 1275000
```

---

## 3. Surcharge Rates

*Applied on Tax Amount (before Cess)*

| Total Income Range | New Regime Rate | Old Regime Rate |
|-------------------|-----------------|-----------------|
| ₹50L - ₹1Cr | 10% | 10% |
| ₹1Cr - ₹2Cr | 15% | 15% |
| ₹2Cr - ₹5Cr | 25% | 25% |
| Above ₹5Cr | **25% (Capped)** | **37%** |

**Health & Education Cess**: 4% (on Tax + Surcharge)

```python
SURCHARGE_NEW = [
    (5000000, 0.00),
    (10000000, 0.10),
    (20000000, 0.15),
    (float('inf'), 0.25),  # Capped at 25%
]

SURCHARGE_OLD = [
    (5000000, 0.00),
    (10000000, 0.10),
    (20000000, 0.15),
    (50000000, 0.25),
    (float('inf'), 0.37),
]

CESS_RATE = 0.04
```

---

## 4. Special Rate Income (No Slabs)

| Type | Section | Rate | Exemption / Notes |
|------|---------|------|-------------------|
| LTCG (Equity) | 112A | **12.5%** | Exemption: ₹1.25 Lakhs/year |
| STCG (Equity) | 111A | **20%** | No Exemption |
| Crypto / VDA | 115BBH | **30%** | Flat Rate. No Deductions. No Set-off |
| Buyback | 2(22)(f) | Slab Rate | Taxed as "Dividend" (IFOS) |
| Presumptive Biz | 44ADA | Slab Rate | Deemed Income = 50% of Receipts |

```python
LTCG_RATE = 0.125
LTCG_EXEMPTION = 125000
STCG_EQUITY_RATE = 0.20
CRYPTO_TAX_RATE = 0.30
CRYPTO_TDS_RATE = 0.01
```

---

## 5. Deduction Limits

### Section 80CCD - NPS

| Section | Description | Limit |
|---------|-------------|-------|
| 80CCD(1) | Employee contribution | Part of ₹1.5L (80C) |
| 80CCD(1B) | Additional personal | ₹50,000 |
| 80CCD(2) | Employer contribution | **14%** of (Basic + DA) - both Pvt & Govt |

> [!NOTE]
> Budget 2025 equalized 80CCD(2) limit to 14% for Private sector (was 10%).

### Section 44ADA - Presumptive Professional

| Condition | Limit |
|-----------|-------|
| Standard Limit | Receipts ≤ ₹50 Lakhs |
| Enhanced Limit | Receipts ≤ **₹75 Lakhs** (if Cash < 5%) |

### Section 24 - House Property

| Deduction | Value |
|-----------|-------|
| Standard Deduction | **30%** of Net Annual Value |
| Interest (Self-Occupied) | ₹2,00,000 (Old Regime only) |
| Interest (Let-Out) | Fully Deductible (HP loss capped at ₹2L set-off) |

```python
MAX_80C = 150000
MAX_80CCD_1B = 50000
MAX_80CCD_2_RATE = 0.14  # 14% for BOTH Pvt & Govt (Budget 2025)

PRESUMPTIVE_44ADA_RATE = 0.50
PRESUMPTIVE_44ADA_LIMIT = 5000000  # ₹50L standard
PRESUMPTIVE_44ADA_ENHANCED = 7500000  # ₹75L (if Cash < 5%)

RENTAL_STANDARD_DEDUCTION = 0.30
HOME_LOAN_INTEREST_SELF_OCCUPIED = 200000
```

---

## 6. Health Insurance (Section 80D)

| Category | Self & Family | Parents |
|----------|--------------|---------|
| Below 60 | ₹25,000 | ₹25,000 |
| Senior Citizen (60+) | ₹50,000 | ₹50,000 |
| Preventive Checkup | ₹5,000 (included) | ₹5,000 (included) |

```python
MAX_80D_SELF = 25000
MAX_80D_SELF_SENIOR = 50000
MAX_80D_PARENTS = 25000
MAX_80D_PARENTS_SENIOR = 50000
```

---

## 7. HRA Exemption

| City Type | Rate |
|-----------|------|
| Metro (Delhi, Mumbai, Chennai, Kolkata) | 50% of (Basic + DA) |
| Non-Metro | 40% of (Basic + DA) |

```python
HRA_METRO_RATE = 0.50
HRA_NON_METRO_RATE = 0.40
METRO_CITIES = ["Delhi", "Mumbai", "Chennai", "Kolkata"]
```

---

## 8. Gift Taxation

| Category | Tax Treatment |
|----------|---------------|
| From Relatives | ✅ Exempt |
| On Marriage | ✅ Exempt |
| From Non-relatives (aggregate > ₹50K) | ❌ Fully Taxable |

---

## 9. Metadata for Validation

```json
{
  "AY": "2026-27",
  "FY": "2025-26",
  "Effective_Date": "2025-04-01",
  "Budget_Version": "Union Budget 2025",
  "Currency": "INR"
}
```

---

## Quick Import Block

```python
TAX_CONSTANTS = {
    # Slabs (Budget 2025 Updated)
    "new_regime_slabs": NEW_REGIME_SLABS,
    "old_regime_slabs": OLD_REGIME_SLABS,
    
    # Standard Deduction
    "standard_deduction_new": 75000,
    "standard_deduction_old": 50000,
    
    # Rebate
    "rebate_87a_new_threshold": 1200000,
    "rebate_87a_new_max": 60000,
    "marginal_relief_ceiling": 1275000,
    
    # Cess
    "cess_rate": 0.04,
    
    # Deductions
    "max_80c": 150000,
    "max_80ccd_1b": 50000,
    "max_80ccd_2_rate": 0.14,
    
    # Capital Gains
    "ltcg_rate": 0.125,
    "ltcg_exemption": 125000,
    "stcg_equity_rate": 0.20,
    
    # Crypto
    "crypto_rate": 0.30,
    
    # FY reference
    "financial_year": "2025-26",
    "assessment_year": "2026-27",
}
```