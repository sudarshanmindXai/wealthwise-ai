def decide_itr(profile):
    reasons = []
    itr = None

    income = profile.get("income", {}) or {}
    flags = profile.get("flags", {}) or {}

    bp = income.get("business_profession", {}) or {}
    cg = income.get("capital_gains", {}) or {}
    hp = income.get("house_property", {}) or {}

    has_business = bp.get("has_business_income", False)
    presumptive = bp.get("presumptive", {}).get("opted", False)
    has_cg = cg.get("has_capital_gains", False)
    hp_count = hp.get("count_properties", 0)
    foreign_assets = flags.get("foreign_assets", False)

    is_director = flags.get("director_in_company", False)
    has_unlisted_equity = flags.get("unlisted_equity_investment", False)

    # ---- Business cases ----
    if has_business and presumptive:
        itr = "ITR-4"
        reasons.append("Presumptive business income selected")

    elif has_business:
        itr = "ITR-3"
        reasons.append("Business or profession income present")

    # ---- Non-business but complex cases ----
    elif (
        has_cg
        or hp_count > 1
        or foreign_assets
        or is_director
        or has_unlisted_equity
    ):
        itr = "ITR-2"
        reasons.append(
            "Capital gains / multiple house properties / foreign assets / director or unlisted equity"
        )

    # ---- Simple cases ----
    else:
        itr = "ITR-1"
        reasons.append("Simple income sources only")

    return itr, reasons