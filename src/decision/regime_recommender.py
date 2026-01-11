import json

from src.compute.tax_engine import (
    compute_taxable_income_old_regime,
    compute_old_regime,
    compute_new_regime
)
from src.decision.itr_selector import decide_itr
from src.decision.missing_info_detector import detect_missing_info
from src.retrieval.basic_retriever import load_chunks, search
from src.explain.explain_regime_choice import explain_regime_choice
from src.llm.llm_adapter import (
    generate_user_explanation,
    generate_followup_questions
)


def recommend_regime(profile):
    """
    Computes tax under old and new regime and recommends the lower tax option.
    """

    # Old regime computation (with deductions)
    old_breakup = compute_taxable_income_old_regime(profile)
    old_tax = compute_old_regime({
        "gross_total_income": old_breakup["taxable_income"]
    })

    # New regime computation (no deductions)
    new_tax = compute_new_regime({
        "gross_total_income": old_breakup["gross_total_income"]
    })

    if new_tax < old_tax:
        regime = "NEW"
    else:
        regime = "OLD"

    return regime, old_tax, new_tax, old_breakup


if __name__ == "__main__":
    # ---------- Load profile ----------
    profile = json.load(open("data/user_profiles/sample_profile_v1.json"))

    # ---------- Step 1: Detect missing info ----------
    missing_info = detect_missing_info(profile)

    # ---------- Step 2: Decide ITR ----------
    itr, reasons = decide_itr(profile)

    # ---------- Step 3: Recommend tax regime ----------
    regime, old_tax, new_tax, old_breakup = recommend_regime(profile)

    # ---------- Step 4: Retrieve legal citations ----------
    chunks = load_chunks()
    citations = search(
        chunks,
        f"{itr} eligibility",
        top_k=3,
        itr_form=itr
    )

    # ---------- Step 5: Deterministic explanation ----------
    explanation_lines = explain_regime_choice(
        old_breakup,
        old_tax,
        new_tax
    )

    # ---------- Step 6: LLM adapter (language only) ----------
    user_explanation = generate_user_explanation(explanation_lines)
    followup_questions = generate_followup_questions(missing_info)

    # ---------- Output ----------
    print("\n=== TAX DECISION SUMMARY ===")

    print("\nRecommended ITR:", itr)
    print("Reasons:")
    for r in reasons:
        print("-", r)

    print("\nTax Computation:")
    print("Gross Total Income:", old_breakup["gross_total_income"])
    print("Old Regime Tax:", old_tax)
    print("New Regime Tax:", new_tax)
    print("Recommended Regime:", regime)

    print("\nExplanation:")
    for line in explanation_lines:
        print("-", line)

    print("\nLLM-style Explanation:")
    print(user_explanation)

    print("\nMissing Information:")
    if not missing_info["required"] and not missing_info["optional"]:
        print("- None")
    else:
        for r in missing_info["required"]:
            print("- REQUIRED:", r)
        for o in missing_info["optional"]:
            print("- OPTIONAL:", o)

    print("\nFollow-up Questions:")
    if not followup_questions:
        print("- None")
    else:
        for q in followup_questions:
            print("-", q)

    print("\nSupporting Citations:")
    for c in citations:
        print("-" * 40)
        print(c["doc_id"], "|", c["file"], "| line", c["line_no"])
        print(c["text"][:300])