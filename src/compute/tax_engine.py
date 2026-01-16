from typing import Dict, Any


def compute_old_regime(income_breakup: Dict[str, Any]) -> float:
    """
    Expects: income_breakup contains "taxable_income_old_regime" (number)
    """
    taxable = float(income_breakup.get("taxable_income_old_regime", 0))
    tax = 0.0

    slabs = [
        (250000, 0.0),
        (500000, 0.05),
        (1000000, 0.20),
        (float("inf"), 0.30),
    ]

    prev_limit = 0.0
    for limit, rate in slabs:
        if taxable <= prev_limit:
            break
        amount = min(taxable, float(limit)) - prev_limit
        tax += amount * rate
        prev_limit = float(limit)

    return round(tax, 2)


def compute_new_regime(income_breakup: Dict[str, Any]) -> float:
    """
    Expects: income_breakup contains "gross_total_income" (number)
    (New regime generally ignores deductions in this simplified engine.)
    """
    taxable = float(income_breakup.get("gross_total_income", 0))
    tax = 0.0

    slabs = [
        (300000, 0.0),
        (600000, 0.05),
        (900000, 0.10),
        (1200000, 0.15),
        (1500000, 0.20),
        (float("inf"), 0.30),
    ]

    prev_limit = 0.0
    for limit, rate in slabs:
        if taxable <= prev_limit:
            break
        amount = min(taxable, float(limit)) - prev_limit
        tax += amount * rate
        prev_limit = float(limit)

    return round(tax, 2)


def compute_taxable_income_old_regime(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Matches your current API payload shape:

    profile = {
      "income": {
        "salary": 1200000,
        "other_income": 0,
        "deductions": {
          "section_80c": 150000,
          ...
        },
        ... (optional sections like house_property/capital_gains/etc.)
      }
    }
    """
    # V1 payload shape: profile['income']
    income = profile.get("income")
    if isinstance(income, dict) and income:
        income = income or {}
        deductions = profile.get("deductions_old_regime") or income.get("deductions") or {}

        # ---- Gross Total Income ----
        salary_raw = income.get("salary", 0)
        if isinstance(salary_raw, dict):
            gross_salary = salary_raw.get("gross_salary", 0) or 0
        else:
            gross_salary = salary_raw or 0

        hp = income.get("house_property", {}) or {}
        hp_income = (hp.get("self_occupied_interest", 0) or 0) + (hp.get("let_out_net_income", 0) or 0)

        cg = income.get("capital_gains", {}) or {}
        capital_gains = (
            (cg.get("stcg_111a", 0) or 0)
            + (cg.get("stcg_other", 0) or 0)
            + (cg.get("ltcg_112a", 0) or 0)
            + (cg.get("ltcg_other", 0) or 0)
        )

        # If you have other_sources dict, sum numeric values; else fall back to simple other_income field
        other_sources = income.get("other_sources", {}) or {}
        other_sources_sum = sum(v for v in other_sources.values() if isinstance(v, (int, float)))
        other_income_simple = income.get("other_income", 0) or 0
        other_income = other_sources_sum if other_sources else other_income_simple

        bp = income.get("business_profession", {}) or {}
        if (bp.get("presumptive", {}) or {}).get("opted"):
            business_income = (bp.get("presumptive", {}) or {}).get("presumptive_income", 0) or 0
        else:
            business_income = (bp.get("non_presumptive", {}) or {}).get("net_profit", 0) or 0

        gross_total_income = float(gross_salary) + float(hp_income) + float(capital_gains) + float(other_income) + float(business_income)

        # ---- Deductions (Old Regime only) ----
        total_deductions = (
            float(deductions.get("section_80c", 0) or deductions.get("80c", 0) or 0)
            + float(deductions.get("80ccd_1b", 0) or 0)
            + float(deductions.get("80d", 0) or 0)
            + float(deductions.get("80tta", 0) or 0)
            + float(deductions.get("80g", 0) or 0)
            + float(deductions.get("other_chapter_via", 0) or 0)
        )
    else:
        # V2 payload shape: TaxFacts (flat fields)
        gross_salary = profile.get("salary_gross", 0) or 0
        letout_income = profile.get("property_letout_net_income", 0) or 0
        home_loan_interest = profile.get("home_loan_interest_paid", 0) or 0
        hp_income = float(letout_income) - float(home_loan_interest)

        capital_gains = (
            float(profile.get("capital_gains_stcg_111a", 0) or 0)
            + float(profile.get("capital_gains_stcg_other", 0) or 0)
            + float(profile.get("capital_gains_ltcg_112a", 0) or 0)
            + float(profile.get("capital_gains_ltcg_other", 0) or 0)
        )

        other_income = (
            float(profile.get("other_income_savings_interest", 0) or 0)
            + float(profile.get("other_income_fd_interest", 0) or 0)
            + float(profile.get("other_income_dividends", 0) or 0)
            + float(profile.get("other_income_family_pension", 0) or 0)
            + float(profile.get("other_income_other", 0) or 0)
        )

        if profile.get("business_has_income"):
            business_income = float(profile.get("business_non_presumptive_profit", 0) or 0)
        else:
            business_income = 0.0

        gross_total_income = float(gross_salary) + float(hp_income) + float(capital_gains) + float(other_income) + float(business_income)

        total_deductions = (
            float(profile.get("deduction_80c", 0) or 0)
            + float(profile.get("deduction_80ccd_1b", 0) or 0)
            + float(profile.get("deduction_80d_self", 0) or 0)
            + float(profile.get("deduction_80tta", 0) or 0)
            + float(profile.get("deduction_80g", 0) or 0)
            + float(profile.get("deduction_other", 0) or 0)
        )

    taxable_income = max(0.0, gross_total_income - total_deductions)

    return {
        "gross_total_income": round(gross_total_income, 2),
        "total_deductions_old_regime": round(total_deductions, 2),
        "taxable_income_old_regime": round(taxable_income, 2),
    }