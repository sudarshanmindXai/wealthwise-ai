from enum import Enum
from typing import Dict, Any

from src.core.recommendation_service import get_tax_recommendation


class AgentIntent(str, Enum):
    TAX_RECOMMENDATION = "tax_recommendation"
    EXPLANATION = "explanation"
    MISSING_INFO = "missing_info"
    CITATIONS = "citations"


def classify_intent(user_query: str) -> AgentIntent:
    """
    Very simple deterministic intent classifier.
    LLM will replace this later.
    """
    q = user_query.lower()

    if "itr" in q or "file" in q or "regime" in q:
        return AgentIntent.TAX_RECOMMENDATION

    if "why" in q or "explain" in q:
        return AgentIntent.EXPLANATION

    if "missing" in q or "need" in q or "document" in q:
        return AgentIntent.MISSING_INFO

    if "law" in q or "section" in q or "citation" in q:
        return AgentIntent.CITATIONS

    return AgentIntent.TAX_RECOMMENDATION


def agent_route(
    user_query: str,
    profile: Dict[str, Any],
    scenarios_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Routes the user request to the correct deterministic capability.
    """

    intent = classify_intent(user_query)

    # Scenario-aware chat: only reference, never recompute
    scenario_keywords = [
        "save more tax", "best options", "top scenario", "recommended", "invest more", "tax saving", "opportunity", "scenarios", "how can i save", "what if i invest", "how much can i save"
    ]
    scenario_intent = any(kw in user_query.lower() for kw in scenario_keywords)

    if scenarios_context and scenario_intent:
        # Reference top 1-3 scenarios
        top_scenarios = scenarios_context.get("top_scenarios", [])
        rec_regime = scenarios_context.get("recommended_regime", "old")
        response_lines = []
        if top_scenarios:
            response_lines.append(f"Based on your profile, here are your top tax-saving opportunities:")
            for i, scenario in enumerate(top_scenarios[:3], 1):
                desc = scenario.get("description", "")
                mod = scenario.get("modification", "")
                regime = scenario.get("recommended_regime", rec_regime)
                saved = scenario.get(f"tax_saved_{regime}_regime", 0)
                try:
                    saved_fmt = f"₹{saved:,.0f}"
                except Exception:
                    saved_fmt = f"₹{saved}"
                response_lines.append(f"• Opportunity {i}: {desc}\n  {mod}\n  Saves {saved_fmt} in the {regime} regime.")
        else:
            response_lines.append("No applicable tax-saving scenarios were found for your profile.")
        return {
            "intent": "scenario_reference",
            "response": "\n".join(response_lines)
        }

    # Fallback: original deterministic behavior
    result = get_tax_recommendation(profile)

    # Custom responses for common user questions to avoid identical replies
    q = user_query.lower()
    if "itr" in q or "file" in q:
        itr = result.get("itr", {}).get("recommended", "ITR-1")
        reasons = result.get("itr", {}).get("reasons", [])
        reasons_txt = "; ".join(reasons) if reasons else "Based on your income sources."
        return {
            "intent": "itr_recommendation",
            "response": f"You should file {itr}. Reason: {reasons_txt}"
        }

    if "save" in q or "invest" in q or "reduce" in q:
        missing = result.get("missing_info", {})
        required = missing.get("required", [])
        optional = missing.get("optional", [])
        tip_lines = []
        if optional:
            tip_lines.append("Potential tax-saving inputs to consider: " + ", ".join(optional) + ".")
        if required:
            tip_lines.append("Required to finalize computation: " + ", ".join(required) + ".")
        if not tip_lines:
            tip_lines.append("Your current inputs already reflect available deductions.")
        return {
            "intent": "tax_saving_guidance",
            "response": " ".join(tip_lines)
        }

    if "80c" in q or "80ccd" in q or "nps" in q or "80d" in q:
        deductions = result.get("income_breakup", {}).get("total_deductions_old_regime", 0)
        return {
            "intent": "deduction_context",
            "response": f"Current total deductions considered under old regime: ₹{deductions:,.0f}. Add/adjust deduction inputs to see updated savings."
        }

    if intent == AgentIntent.EXPLANATION:
        return {
            "intent": intent,
            "explanation": result["explanation"]
        }

    if intent == AgentIntent.MISSING_INFO:
        return {
            "intent": intent,
            "missing_info": result["missing_info"],
            "followup_questions": result["followup_questions"]
        }

    if intent == AgentIntent.CITATIONS:
        return {
            "intent": intent,
            "citations": result["citations"]
        }

    # Default: full recommendation
    return {
        "intent": intent,
        "recommendation": result
    }