def explain_regime_choice(old_breakup, old_tax, new_tax):
    explanation = []

    explanation.append(
        f"Gross total income is ₹{old_breakup['gross_total_income']:,}."
    )

    if old_breakup["total_deductions_old_regime"] > 0:
        explanation.append(
            f"Under the old regime, deductions of ₹{old_breakup['total_deductions_old_regime']:,} "
            f"reduce taxable income to ₹{old_breakup['taxable_income_old_regime']:,}."
        )
    else:
        explanation.append(
            "No deductions are claimed under the old regime."
        )

    explanation.append(
        f"Old regime tax works out to ₹{old_tax:,}."
    )

    explanation.append(
        f"New regime tax works out to ₹{new_tax:,} due to lower slab rates."
    )

    if new_tax < old_tax:
        explanation.append(
            "The new regime results in a lower tax liability and is therefore recommended."
        )
    else:
        explanation.append(
            "The old regime results in a lower tax liability and is therefore recommended."
        )

    return explanation