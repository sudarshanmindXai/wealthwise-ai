from __future__ import annotations
from typing import Any, Dict, List

from src.decision.itr_selector import decide_itr
from src.decision.missing_info_detector import detect_missing_info
from src.compute.tax_engine import (
    compute_taxable_income_old_regime,
    compute_old_regime,
    compute_new_regime,
)
from src.explain.explain_regime_choice import explain_regime_choice
from src.llm.llm_adapter import generate_user_explanation, generate_followup_questions
from src.retrieval.basic_retriever import load_chunks, search
from src.core.audit_logger import log_audit_event


def get_tax_recommendation(profile: Dict[str, Any]) -> Dict[str, Any]:
    missing_info = detect_missing_info(profile)
    itr, itr_reasons = decide_itr(profile)

    old_breakup = compute_taxable_income_old_regime(profile)

    old_tax = compute_old_regime(
        {"taxable_income_old_regime": old_breakup["taxable_income_old_regime"]}
    )

    new_tax = compute_new_regime(
        {"gross_total_income": old_breakup["gross_total_income"]}
    )

    regime = "NEW" if new_tax < old_tax else "OLD"

    explanation_lines = explain_regime_choice(old_breakup, old_tax, new_tax)
    user_explanation = generate_user_explanation(explanation_lines)
    followup_questions = generate_followup_questions(missing_info)

    chunks = load_chunks()
    citations_raw = search(chunks, f"{itr} eligibility", top_k=3, itr_form=itr)
    citations: List[Dict[str, Any]] = [
        {
            "doc_id": c.get("doc_id"),
            "file": c.get("file"),
            "line_no": c.get("line_no"),
            "text_preview": (c.get("text") or "")[:300],
        }
        for c in citations_raw
    ]

    # 🔍 Audit trail
    request_id = profile.get("_request_id", "unknown")
    log_audit_event(
        request_id=request_id,
        profile=profile,
        itr=itr,
        regime=regime,
        old_tax=old_tax,
        new_tax=new_tax,
        income_breakup=old_breakup,
    )

    return {
        "itr": {
            "recommended": itr,
            "reasons": itr_reasons,
        },
        "regime": {
            "recommended": regime,
            "old_tax": old_tax,
            "new_tax": new_tax,
        },
        "income_breakup": {
            "gross_total_income": old_breakup["gross_total_income"],
            "total_deductions_old_regime": old_breakup["total_deductions_old_regime"],
            "taxable_income_old_regime": old_breakup["taxable_income_old_regime"],
        },
        "explanation": {
            "bullets": explanation_lines,
            "user_friendly": user_explanation,
        },
        "missing_info": missing_info,
        "followup_questions": followup_questions,
        "citations": citations,
    }