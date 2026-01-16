def detect_missing_info(profile):
    missing_required = []
    missing_optional = []

    income = profile.get("income", {}) or {}
    flags = profile.get("flags", {}) or {}

    # V1 format
    if isinstance(income, dict) and income:
        deductions = income.get("deductions", {}) or {}

        # ---------- Salary ----------
        salary = income.get("salary")
        if salary is None:
            missing_required.append("Gross salary amount")

        # ---------- House Property ----------
        hp = income.get("house_property", {}) or {}
        if hp.get("count_properties", 0) > 0:
            if hp.get("self_occupied_interest", 0) == 0:
                missing_optional.append("Home loan interest certificate (Section 24)")

        # ---------- Deductions (Old Regime) ----------
        if deductions.get("section_80c", 0) == 0:
            missing_optional.append("Section 80C investment details (if any)")

        if deductions.get("80d", 0) == 0:
            missing_optional.append("Section 80D medical insurance details (if any)")

        # ---------- Capital Gains ----------
        cg = income.get("capital_gains", {}) or {}
        if cg.get("has_capital_gains"):
            total_cg = (
                cg.get("stcg_111a", 0)
                + cg.get("stcg_other", 0)
                + cg.get("ltcg_112a", 0)
                + cg.get("ltcg_other", 0)
            )
            if total_cg == 0:
                missing_required.append("Capital gains breakup details")

        # ---------- Foreign Assets ----------
        if flags.get("foreign_assets"):
            missing_required.append("Foreign asset / income disclosure details")
    else:
        # V2 TaxFacts format
        if float(profile.get("salary_gross", 0) or 0) == 0:
            missing_required.append("Gross salary amount")

        if int(profile.get("property_count", 0) or 0) > 0:
            if float(profile.get("home_loan_interest_paid", 0) or 0) == 0:
                missing_optional.append("Home loan interest certificate (Section 24)")

        if float(profile.get("deduction_80c", 0) or 0) == 0:
            missing_optional.append("Section 80C investment details (if any)")

        if float(profile.get("deduction_80d_self", 0) or 0) == 0:
            missing_optional.append("Section 80D medical insurance details (if any)")

    return {
        "required": missing_required,
        "optional": missing_optional,
    }