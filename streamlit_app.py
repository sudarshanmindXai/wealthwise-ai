# streamlit_app.py - WealthWise AI v2.0
# Professional Tax Intelligence Platform

from __future__ import annotations

import json
import io
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st
import openai

# Document ingestion imports
try:
    from src.ingest.document_detector import detect_document_type, DocumentType
    from src.ingest.universal_extractor import extract_document_data, map_extracted_to_taxfacts
    DOCUMENT_UPLOAD_ENABLED = True
except ImportError:
    DOCUMENT_UPLOAD_ENABLED = False

# =====================================================================
# Config
# =====================================================================
DEFAULT_API_BASE = "http://127.0.0.1:8000"
TIMEOUT_SECS = 30

# OpenRouter API Key for document detection
OPENROUTER_API_KEY = "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"

# =====================================================================
# Page setup
# =====================================================================
st.set_page_config(
    page_title="WealthWise AI — Tax Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🛡️"
)

# =====================================================================
# Styling — WealthWise Design System (Dark Mode Finance-Grade)
# =====================================================================
st.markdown(
    """
<style>
/* ========== WEALTHWISE DESIGN SYSTEM ========== */

.stApp {
  background: #0F172A;
  color: #F8FAFC;
}
.block-container {
  padding: 0.5rem 1.5rem !important;
  max-width: 1600px !important;
}
.main .block-container { padding-top: 0.5rem !important; }
section[data-testid="stSidebar"] { display: none !important; }

h1, h2, h3 {
  font-family: 'Inter', sans-serif !important;
  color: #F8FAFC !important;
  letter-spacing: -0.5px !important;
  font-weight: 700 !important;
}
h1 { font-size: 1.5rem !important; margin: 0 0 0.3rem 0 !important; }
h2 { font-size: 1.1rem !important; margin: 0.5rem 0 0.3rem 0 !important; }
h3 { font-size: 0.95rem !important; margin: 0.3rem 0 !important; }

p, li, label, span, div {
  font-family: 'Roboto', sans-serif !important;
  color: #CBD5E1;
  line-height: 1.4;
  font-size: 0.9rem;
}

code, .stCode, .stCodeBlock {
  font-family: 'JetBrains Mono', monospace !important;
  background: #1E293B;
  color: #10B981;
}

.ww-topbar {
  background: #1E293B;
  border-bottom: 1px solid #334155;
  padding: 0.8rem 1.5rem;
  margin: -0.5rem -1.5rem 1rem -1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ww-topbar-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
}
.ww-topbar-subtitle {
  font-size: 0.85rem;
  color: #94A3B8;
  margin: 0;
}

.ww-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.ww-badge-regime-old { background: #3B82F6; color: #F8FAFC; }
.ww-badge-regime-new { background: #10B981; color: #F8FAFC; }
.ww-badge-info { background: #3B82F6; color: #F8FAFC; }
.ww-badge-danger { background: #EF4444; color: #F8FAFC; }

.ww-card {
  background: #1E293B;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  margin-bottom: 0.8rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.ww-card-audit { border-left: 4px solid #EF4444; }
.ww-card-secure { border-left: 4px solid #10B981; }
.ww-card-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #F8FAFC;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.ww-extracted-field {
    padding: 0.4rem 0;
    border-bottom: 1px solid #334155;
}
.ww-extracted-label {
    font-size: 0.75rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.ww-extracted-value {
    font-size: 0.9rem;
    color: #E2E8F0;
    font-weight: 600;
}
.ww-extracted-source {
    font-size: 0.75rem;
    color: #94A3B8;
}
.ww-confidence-high { color: #10B981; }
.ww-confidence-medium { color: #F59E0B; }
.ww-confidence-low { color: #EF4444; }

.ww-step {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 6px;
  background: #0F172A;
  border: 1px solid #334155;
  margin-bottom: 0.3rem;
  justify-content: center;
  gap: 0.4rem;
}
.ww-step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #334155;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}
.ww-step-label {
  font-size: 0.85rem;
  color: #94A3B8;
  font-weight: 500;
  white-space: nowrap;
}
.ww-step-active { background: rgba(59, 130, 246, 0.1); border-color: #3B82F6; }
.ww-step-active .ww-step-number { background: #3B82F6; color: #F8FAFC; }
.ww-step-active .ww-step-label { color: #3B82F6; font-weight: 600; }
.ww-step-done { background: rgba(16, 185, 129, 0.1); border-color: #10B981; }
.ww-step-done .ww-step-number { background: #10B981; color: #F8FAFC; }
.ww-step-done .ww-step-label { color: #10B981; }

input, textarea {
  background: #1E293B !important;
  border: 1px solid #334155 !important;
  border-radius: 6px !important;
  padding: 0.4rem 0.6rem !important;
  font-size: 0.9rem !important;
  color: #F8FAFC !important;
  caret-color: #3B82F6 !important;
}
input:focus, textarea:focus {
  border-color: #3B82F6 !important;
  box-shadow: 0 0 0 1px #3B82F6 !important;
}
label[data-testid="stWidgetLabel"] {
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  color: #E2E8F0 !important;
  margin-bottom: 0.2rem !important;
}
div[data-baseweb="select"] > div {
  background: #1E293B !important;
  border: 1px solid #334155 !important;
  border-radius: 6px !important;
  min-height: 38px !important;
  color: #F8FAFC !important;
}

div.stButton > button[kind="primary"] {
  background: #10B981 !important;
  border: 0;
  color: #F8FAFC !important;
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.3);
  height: 42px;
}
div.stButton > button[kind="primary"] * { color: #F8FAFC !important; }
div.stButton > button[kind="primary"]:hover {
  background: #059669 !important;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.4);
}
div.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid #334155 !important;
  color: #E2E8F0 !important;
  font-weight: 500;
}
div.stButton > button[kind="secondary"] * { color: #E2E8F0 !important; }

.ww-result-main {
  background: #1E293B;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1.2rem;
  margin-bottom: 0.8rem;
  text-align: center;
}
.ww-result-label {
  font-size: 0.75rem;
  color: #E2E8F0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  margin-bottom: 0.3rem;
}
.ww-result-value {
  font-size: 2rem;
  font-weight: 700;
  color: #F8FAFC;
  line-height: 1.1;
  font-family: 'JetBrains Mono', monospace !important;
}
.ww-result-value-green { color: #10B981; }
.ww-result-value-red { color: #EF4444; }
.ww-result-subtext {
  font-size: 0.8rem;
  color: #CBD5E1;
  margin-top: 0.3rem;
}

section[data-testid="stFileUploader"] {
  background: #1E293B;
  border: 2px dashed #334155;
  border-radius: 8px;
  padding: 1rem;
}
section[data-testid="stFileUploader"]:hover { border-color: #3B82F6; }

section[data-testid="stExpander"] > details > summary {
  padding: 0.6rem 0.8rem !important;
  line-height: 1.4 !important;
  font-size: 0.9rem !important;
  color: #E2E8F0 !important;
}
section[data-testid="stExpander"] summary p { margin: 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# Helpers
# =====================================================================
def rupee(n: Any) -> str:
    try:
        n = float(n)
        n = f"{n:,.2f}"
    except Exception:
        pass
    return f"₹ {n}"

def safe_get(d: dict, path: List[str], default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def api_post(api_base: str, path: str, payload: dict) -> Tuple[int, dict]:
    url = f"{api_base.rstrip('/')}{path}"
    r = requests.post(url, json=payload, timeout=TIMEOUT_SECS)
    try:
        data = r.json()
    except Exception:
        data = {"detail": r.text}
    return r.status_code, data

def api_health(api_base: str) -> bool:
    try:
        url = f"{api_base.rstrip('/')}/health"
        r = requests.get(url, timeout=6)
        return r.status_code == 200
    except Exception:
        return False

def build_taxprofile_v2(stage1: Dict, stage2: Dict, stage3: Dict, stage4: Dict, user_id: str = "") -> Dict[str, Any]:
    tax_facts_input = {}

    if stage1.get("assessment_year"):
        tax_facts_input["assessment_year"] = stage1["assessment_year"]

    if stage1.get("residential_status"):
        status_map = {"resident_india": "resident", "non_resident": "nri"}
        tax_facts_input["residential_status"] = status_map.get(stage1["residential_status"], "resident")

    age = stage1.get("age", 30)
    if age >= 80:
        tax_facts_input["age_category"] = "above_80"
    elif age >= 60:
        tax_facts_input["age_category"] = "senior_60_80"
    else:
        tax_facts_input["age_category"] = "below_60"

    if stage1.get("salary_gross") is not None:
        tax_facts_input["salary_gross"] = float(stage1["salary_gross"])
    if stage1.get("taxes_paid_tds") is not None:
        tax_facts_input["taxes_tds"] = float(stage1["taxes_paid_tds"])

    if stage1.get("other_income_savings_interest") is not None:
        tax_facts_input["other_income_savings_interest"] = float(stage1["other_income_savings_interest"])
    if stage1.get("other_income_fd_interest") is not None:
        tax_facts_input["other_income_fd_interest"] = float(stage1["other_income_fd_interest"])
    if stage1.get("other_income_dividends") is not None:
        tax_facts_input["other_income_dividends"] = float(stage1["other_income_dividends"])
    if stage1.get("other_income_other") is not None:
        tax_facts_input["other_income_other"] = float(stage1["other_income_other"])

    if stage1.get("capital_gains_stcg_111a") is not None:
        tax_facts_input["capital_gains_stcg_111a"] = float(stage1["capital_gains_stcg_111a"])
    if stage1.get("capital_gains_stcg_other") is not None:
        tax_facts_input["capital_gains_stcg_other"] = float(stage1["capital_gains_stcg_other"])
    if stage1.get("capital_gains_ltcg_112a") is not None:
        tax_facts_input["capital_gains_ltcg_112a"] = float(stage1["capital_gains_ltcg_112a"])
    if stage1.get("capital_gains_ltcg_other") is not None:
        tax_facts_input["capital_gains_ltcg_other"] = float(stage1["capital_gains_ltcg_other"])

    if stage1.get("business_has_income") is not None:
        tax_facts_input["business_has_income"] = bool(stage1.get("business_has_income"))
    if stage1.get("business_non_presumptive_profit") is not None:
        tax_facts_input["business_non_presumptive_profit"] = float(stage1["business_non_presumptive_profit"])

    if stage2.get("has_home_loan") and stage2.get("home_loan_interest_paid"):
        tax_facts_input["home_loan_interest_paid"] = float(stage2["home_loan_interest_paid"])
        tax_facts_input["home_loan_amount"] = float(stage2.get("home_loan_amount", 0))

    if stage2.get("has_investments"):
        if stage2.get("deduction_80c_total"):
            tax_facts_input["deduction_80c"] = float(stage2["deduction_80c_total"])
        if stage2.get("deduction_80ccd_1b_nps"):
            tax_facts_input["deduction_80ccd_1b"] = float(stage2["deduction_80ccd_1b_nps"])
        if stage2.get("deduction_80d_self"):
            tax_facts_input["deduction_80d_self"] = float(stage2["deduction_80d_self"])

    if stage2.get("has_rental"):
        if stage2.get("rental_income"):
            tax_facts_input["property_letout_net_income"] = float(stage2["rental_income"])
        if stage2.get("property_count"):
            tax_facts_input["property_count"] = int(stage2["property_count"])

    user_identity = {}
    if stage1.get("user_full_name"):
        user_identity["full_name"] = stage1.get("user_full_name")

    return {
        "profile_version": "v2",
        "assessment_year": stage1.get("assessment_year", "2024-25"),
        "tax_facts_input": tax_facts_input,
        "user_identity": user_identity,
        "document_payloads": None,
        "chat_clarifications": None,
    }

def build_review_summary(reco: Dict[str, Any], stage1: Dict[str, Any], stage2: Dict[str, Any], scenario_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    regime = safe_get(reco, ["regime", "recommended"], "OLD").upper()
    old_tax = safe_get(reco, ["regime", "old_tax"], 0)
    new_tax = safe_get(reco, ["regime", "new_tax"], 0)
    itr = safe_get(reco, ["itr", "recommended"], "ITR-1")
    gross = safe_get(reco, ["income_breakup", "gross_total_income"], 0)
    deductions = safe_get(reco, ["income_breakup", "total_deductions_old_regime"], 0)
    taxable = safe_get(reco, ["income_breakup", "taxable_income_old_regime"], 0)

    insights = safe_get(reco, ["explanation", "bullets"], []) or []
    savings = max(0, (old_tax - new_tax) if regime == "NEW" else (new_tax - old_tax))

    future_pointers = []
    if stage2.get("has_investments") and stage2.get("deduction_80c_total", 0) < 150000:
        remaining = 150000 - float(stage2.get("deduction_80c_total", 0))
        future_pointers.append(f"Consider utilising remaining 80C capacity of ₹{remaining:,.0f} before year-end.")
    if stage2.get("deduction_80ccd_1b_nps", 0) < 50000:
        remaining = 50000 - float(stage2.get("deduction_80ccd_1b_nps", 0))
        future_pointers.append(f"You can contribute up to ₹{remaining:,.0f} more under 80CCD(1B) (NPS).")
    if stage2.get("deduction_80d_self", 0) == 0:
        future_pointers.append("If you have health insurance, add 80D premium details to reduce tax.")
    if stage2.get("has_rental") and stage2.get("rental_income", 0) > 0 and stage2.get("property_count", 0) > 0:
        future_pointers.append("Keep rental agreements and interest certificates for future filings.")

    if not future_pointers:
        future_pointers.append("Your current inputs already reflect most common deductions. Keep documents updated for next year.")

    top_scenarios = scenario_data.get("top_scenarios", []) if scenario_data else []
    scenario_notes = []
    for s in top_scenarios[:3]:
        scenario_notes.append(f"{s.get('description', 'Scenario')} — {s.get('modification', '')}")

    return {
        "headline": f"Recommended: {regime} regime | {itr}",
        "summary": f"Gross income ₹{gross:,.0f}, deductions ₹{deductions:,.0f}, taxable ₹{taxable:,.0f}. Old tax ₹{old_tax:,.0f}, New tax ₹{new_tax:,.0f}.",
        "insights": insights,
        "future_pointers": future_pointers,
        "scenario_notes": scenario_notes,
        "savings": savings,
    }

def generate_ai_summary(summary: Dict[str, Any], api_key: Optional[str]) -> Optional[str]:
    if not api_key:
        return None
    try:
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        prompt = (
            "Create a concise tax review summary with bullet points and next-year pointers. "
            "Use the provided data only.\n\n"
            f"Headline: {summary.get('headline')}\n"
            f"Summary: {summary.get('summary')}\n"
            f"Insights: {summary.get('insights')}\n"
            f"Future pointers: {summary.get('future_pointers')}\n"
            f"Scenarios: {summary.get('scenario_notes')}\n"
        )
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None

# =====================================================================
# Session State
# =====================================================================
if "stage1" not in st.session_state:
    st.session_state["stage1"] = {
        "assessment_year": "2024-25",
        "residential_status": "resident_india",
        "age": 30,
        "salary_gross": 1500000.0,
        "taxes_paid_tds": 150000.0,
        "other_income_savings_interest": 0.0,
        "other_income_fd_interest": 0.0,
        "other_income_dividends": 0.0,
        "other_income_other": 0.0,
        "capital_gains_stcg_111a": 0.0,
        "capital_gains_stcg_other": 0.0,
        "capital_gains_ltcg_112a": 0.0,
        "capital_gains_ltcg_other": 0.0,
        "business_has_income": False,
        "business_non_presumptive_profit": 0.0,
        "user_full_name": "",
    }

if "stage2" not in st.session_state:
    st.session_state["stage2"] = {
        "has_home_loan": False,
        "home_loan_interest_paid": 0,
        "home_loan_amount": 0,
        "has_investments": False,
        "deduction_80c_total": 0,
        "deduction_80ccd_1b_nps": 0,
        "deduction_80d_self": 0,
        "has_rental": False,
        "rental_income": 0,
        "property_count": 0,
    }

if "last_reco" not in st.session_state:
    st.session_state["last_reco"] = None

if "current_stage" not in st.session_state:
    st.session_state["current_stage"] = 1

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 1

if "income_types" not in st.session_state:
    st.session_state["income_types"] = {
        "salaried": True,
        "business": False,
        "other": False,
    }

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "show_analyzing" not in st.session_state:
    st.session_state["show_analyzing"] = False

# Migrate old session defaults
DEFAULTS_VERSION = 2
if "defaults_version" not in st.session_state:
    st.session_state["defaults_version"] = 0
if st.session_state["defaults_version"] < DEFAULTS_VERSION:
    stage1_current = st.session_state.get("stage1", {})
    if stage1_current.get("salary_gross", 0) == 0 and stage1_current.get("taxes_paid_tds", 0) == 0:
        st.session_state["stage1"] = {
            "assessment_year": "2024-25",
            "residential_status": "resident_india",
            "age": 30,
            "salary_gross": 1500000.0,
            "taxes_paid_tds": 150000.0,
            "other_income_savings_interest": 0.0,
            "other_income_fd_interest": 0.0,
            "other_income_dividends": 0.0,
            "other_income_other": 0.0,
            "capital_gains_stcg_111a": 0.0,
            "capital_gains_stcg_other": 0.0,
            "capital_gains_ltcg_112a": 0.0,
            "capital_gains_ltcg_other": 0.0,
            "business_has_income": False,
            "business_non_presumptive_profit": 0.0,
            "user_full_name": "",
        }
        st.session_state["last_reco"] = None
    st.session_state["defaults_version"] = DEFAULTS_VERSION

# =====================================================================
# API Connection
# =====================================================================
api_base = DEFAULT_API_BASE
is_up = api_health(api_base)

# =====================================================================
# TOP BAR
# =====================================================================
reco = st.session_state.get("last_reco")
recommended_regime = safe_get(reco, ["regime", "recommended"], "").upper() if reco else ""

regime_badge = ""
if recommended_regime == "OLD":
    regime_badge = '<span class="ww-badge ww-badge-regime-old">OLD REGIME</span>'
elif recommended_regime == "NEW":
    regime_badge = '<span class="ww-badge ww-badge-regime-new">NEW REGIME</span>'

st.markdown(
    f"""
<div class="ww-topbar">
  <div style="flex: 1; text-align: center;">
    <div class="ww-topbar-title">WealthWise</div>
    <div class="ww-topbar-subtitle">Tax planning made simple</div>
  </div>
  <div style="position: absolute; right: 1.5rem;">{regime_badge}</div>
</div>
""",
    unsafe_allow_html=True
)

# Persistent reset button
col_reset1, col_reset2, col_reset3 = st.columns([2, 1, 2])
with col_reset2:
    if st.button("🔄 Reset Form & Reload Defaults", use_container_width=True, key="reset_session"):
        keys_to_clear = [
            "stage1", "stage2", "last_reco", "current_stage",
            "active_tab", "income_types", "chat_history",
            "scenario_data", "scenario_error", "review_ai_summary",
            "extracted_data", "update_success", "update_error",
            "show_analyzing", "chat_input", "clear_chat_input",
        ]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state["active_tab"] = 1
        st.session_state["current_stage"] = 1
        st.rerun()

# =====================================================================
# 4-TAB LAYOUT
# =====================================================================
def is_income_valid() -> bool:
    s1_local = st.session_state.get("stage1", {})
    types = st.session_state.get("income_types", {})
    valid = False
    if types.get("salaried") and float(s1_local.get("salary_gross", 0) or 0) > 0:
        valid = True
    if types.get("business") and float(s1_local.get("business_non_presumptive_profit", 0) or 0) > 0:
        valid = True
    if types.get("other"):
        other_sum = (
            float(s1_local.get("other_income_savings_interest", 0) or 0)
            + float(s1_local.get("other_income_fd_interest", 0) or 0)
            + float(s1_local.get("other_income_dividends", 0) or 0)
            + float(s1_local.get("other_income_other", 0) or 0)
            + float(s1_local.get("capital_gains_stcg_111a", 0) or 0)
            + float(s1_local.get("capital_gains_stcg_other", 0) or 0)
            + float(s1_local.get("capital_gains_ltcg_112a", 0) or 0)
            + float(s1_local.get("capital_gains_ltcg_other", 0) or 0)
        )
        valid = valid or other_sum > 0
    return valid

def is_user_valid() -> bool:
    s1_local = st.session_state.get("stage1", {})
    return bool(s1_local.get("assessment_year")) and int(s1_local.get("age", 0) or 0) >= 18

def is_deductions_ready() -> bool:
    return st.session_state.get("last_reco") is not None

active_tab = st.session_state.get("active_tab", 1)
income_done = is_income_valid()
user_done = is_user_valid()
deductions_done = is_deductions_ready()

stepper_html = """
<div class="ww-card" style="padding:0.6rem 0.8rem;">
  <div style="display:flex;gap:0.6rem;justify-content:space-between;">
"""
tab_labels = ["Income", "User Details", "Deductions & Optimize", "Chat & Review"]
for i, label in enumerate(tab_labels, start=1):
    cls = "ww-step"
    if i < active_tab:
        cls += " ww-step-done"
    elif i == active_tab:
        cls += " ww-step-active"
    icon = "✓" if i < active_tab else str(i)
    stepper_html += f"<div class='{cls}' style='flex:1;justify-content:center;'><div class='ww-step-number'>{icon}</div><div class='ww-step-label'>{label}</div></div>"
stepper_html += "</div></div>"
st.markdown(stepper_html, unsafe_allow_html=True)

nav_cols = st.columns(4)
for i, col in enumerate(nav_cols, start=1):
    can_go = True
    if i > active_tab:
        if active_tab == 1 and not income_done:
            can_go = False
        if active_tab == 2 and not user_done:
            can_go = False
        if active_tab == 3 and not deductions_done:
            can_go = False
    label = tab_labels[i - 1]
    if col.button(label, key=f"nav_tab_{i}"):
        if can_go or i <= active_tab:
            st.session_state["active_tab"] = i
            st.rerun()
        else:
            st.warning("Complete the current step before moving forward.")

st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

if active_tab == 1:
    st.markdown('<div class="ww-card">', unsafe_allow_html=True)
    st.markdown('<div class="ww-card-title">WealthWise</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top:0.2rem;">Let\'s decode your Financial Fingerprint.</h2>', unsafe_allow_html=True)
    st.markdown('<p>Select all that apply. We\'ll reveal your personalized tax strategy.</p>', unsafe_allow_html=True)

    tcols = st.columns(3)
    with tcols[0]:
        st.session_state["income_types"]["salaried"] = st.checkbox("Salaried Job", value=st.session_state["income_types"].get("salaried", True), key="income_salaried")
    with tcols[1]:
        st.session_state["income_types"]["business"] = st.checkbox("Business / Freelance", value=st.session_state["income_types"].get("business", False), key="income_business")
    with tcols[2]:
        st.session_state["income_types"]["other"] = st.checkbox("Other Income", value=st.session_state["income_types"].get("other", False), key="income_other")

    s1 = st.session_state["stage1"]
    if st.session_state["income_types"].get("salaried"):
        st.markdown('<div class="ww-card" style="margin-top:0.8rem;">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">Salaried Job</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            s1["salary_gross"] = st.number_input("Gross Salary (₹)", min_value=0.0, value=float(s1.get("salary_gross", 0.0)), step=10000.0, format="%.2f", key="inp_salary")
        with c2:
            s1["taxes_paid_tds"] = st.number_input("TDS Paid (₹)", min_value=0.0, value=float(s1.get("taxes_paid_tds", 0.0)), step=10000.0, format="%.2f", key="inp_tds")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["income_types"].get("business"):
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">Business / Freelance</div>', unsafe_allow_html=True)
        s1["business_has_income"] = True
        s1["business_non_presumptive_profit"] = st.number_input("Net Profit (₹)", min_value=0.0, value=float(s1.get("business_non_presumptive_profit", 0.0)), step=10000.0, format="%.2f", key="biz_profit")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["income_types"].get("other"):
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">Other Income</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            s1["other_income_savings_interest"] = st.number_input("Savings Interest (₹)", min_value=0.0, value=float(s1.get("other_income_savings_interest", 0.0)), step=1000.0, format="%.2f", key="other_sav")
            s1["other_income_dividends"] = st.number_input("Dividends (₹)", min_value=0.0, value=float(s1.get("other_income_dividends", 0.0)), step=1000.0, format="%.2f", key="other_div")
        with c2:
            s1["other_income_fd_interest"] = st.number_input("FD Interest (₹)", min_value=0.0, value=float(s1.get("other_income_fd_interest", 0.0)), step=1000.0, format="%.2f", key="other_fd")
            s1["other_income_other"] = st.number_input("Other Income (₹)", min_value=0.0, value=float(s1.get("other_income_other", 0.0)), step=1000.0, format="%.2f", key="other_misc")
        st.markdown('<div class="ww-card-title" style="margin-top:0.6rem;">Capital Gains</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            s1["capital_gains_stcg_111a"] = st.number_input("STCG 111A (₹)", min_value=0.0, value=float(s1.get("capital_gains_stcg_111a", 0.0)), step=1000.0, format="%.2f", key="cg_stcg_111a")
            s1["capital_gains_ltcg_112a"] = st.number_input("LTCG 112A (₹)", min_value=0.0, value=float(s1.get("capital_gains_ltcg_112a", 0.0)), step=1000.0, format="%.2f", key="cg_ltcg_112a")
        with c4:
            s1["capital_gains_stcg_other"] = st.number_input("STCG Other (₹)", min_value=0.0, value=float(s1.get("capital_gains_stcg_other", 0.0)), step=1000.0, format="%.2f", key="cg_stcg_other")
            s1["capital_gains_ltcg_other"] = st.number_input("LTCG Other (₹)", min_value=0.0, value=float(s1.get("capital_gains_ltcg_other", 0.0)), step=1000.0, format="%.2f", key="cg_ltcg_other")
        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state["stage1"] = s1

    if st.button("Continue to User Details", type="primary", use_container_width=True, key="btn_to_user"):
        if is_income_valid():
            st.session_state["active_tab"] = 2
            st.rerun()
        else:
            st.error("Please enter at least one valid income value.")

    st.markdown('</div>', unsafe_allow_html=True)

elif active_tab == 2:
    st.markdown('<div class="ww-card">', unsafe_allow_html=True)
    st.markdown('<div class="ww-card-title">WealthWise</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top:0.2rem;">User Details</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="ww-card ww-card-secure">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">Secure Document Upload</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.8rem;">Upload your documents for analysis. All data is processed locally.</p>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#10B981;margin-bottom:0.6rem;">PII scrubbed and personal data removed locally. Your privacy is protected.</div>', unsafe_allow_html=True)

        bank_files = st.file_uploader("Bank Statement (PDF/CSV)", type=["pdf", "csv"], accept_multiple_files=False, key="upload_bank")
        form16_files = st.file_uploader("Form 16 (PDF)", type=["pdf"], accept_multiple_files=False, key="upload_form16")

        uploaded_files = []
        if bank_files:
            uploaded_files.append(bank_files)
        if form16_files:
            uploaded_files.append(form16_files)

        if DOCUMENT_UPLOAD_ENABLED and uploaded_files:
            if "extracted_data" not in st.session_state:
                st.session_state["extracted_data"] = {}

            for uploaded_file in uploaded_files:
                file_key = f"{uploaded_file.name}_{uploaded_file.size}"
                if file_key in st.session_state["extracted_data"]:
                    continue

                with st.spinner(f"🔍 Analyzing {uploaded_file.name}..."):
                    try:
                        from src.ingest.document_detector import detect_document_type, DocumentType
                        from src.ingest.universal_extractor import extract_document_data, map_extracted_to_taxfacts

                        file_bytes = uploaded_file.getvalue()
                        filename = uploaded_file.name
                        file_extension = filename.split(".")[-1].lower() if "." in filename else ""

                        if file_extension == "csv":
                            detection_result = {
                                "document_type": DocumentType.BANK_STATEMENT.value,
                                "confidence": 1.0,
                                "reasoning": "CSV upload assumed to be a bank statement",
                                "suggestions": []
                            }
                        else:
                            detection_result = detect_document_type(file_bytes, filename, file_extension)

                        if detection_result["document_type"] == "unknown":
                            st.warning(f"⚠️ Could not identify {uploaded_file.name}. Please check the file format.")
                            continue

                        extraction_result = extract_document_data(
                            file_bytes,
                            DocumentType(detection_result["document_type"]),
                            filename,
                            file_extension
                        )

                        mapped_data = map_extracted_to_taxfacts(
                            extraction_result["extracted_data"],
                            DocumentType(detection_result["document_type"])
                        )

                        st.session_state["extracted_data"][file_key] = {
                            "filename": uploaded_file.name,
                            "doc_type": detection_result["document_type"],
                            "confidence": detection_result["confidence"],
                            "extracted": extraction_result["extracted_data"],
                            "mapped": mapped_data,
                            "warnings": extraction_result.get("warnings", [])
                        }

                        st.success(f"✅ Extracted data from {uploaded_file.name} (Type: {detection_result['document_type']}, Confidence: {detection_result['confidence']:.0%})")
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

            if st.session_state.get("extracted_data"):
                st.markdown('<div style="margin-top:0.6rem;"><strong style="font-size:0.85rem;">Extracted Data:</strong></div>', unsafe_allow_html=True)
                for file_key, file_data in st.session_state["extracted_data"].items():
                    with st.expander(f"📋 {file_data['filename']} ({file_data['doc_type']})"):
                        for field_name, field_value in file_data["extracted"].items():
                            if field_value:
                                confidence_class = "ww-confidence-high" if file_data["confidence"] > 0.8 else "ww-confidence-medium" if file_data["confidence"] > 0.5 else "ww-confidence-low"
                                st.markdown(
                                    f'<div class="ww-extracted-field">'
                                    f'<div class="ww-extracted-label">{field_name.replace("_", " ").title()}</div>'
                                    f'<div class="ww-extracted-value">{field_value}</div>'
                                    f'<div class="ww-extracted-source">Source: {file_data["filename"]} | '
                                    f'<span class="{confidence_class}">Confidence: {file_data["confidence"]:.0%}</span></div>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )

                        if file_data.get("warnings"):
                            st.warning("⚠️ " + " | ".join(file_data["warnings"]))

                        if st.button("Apply to Form", key=f"apply_{file_key}"):
                            mapped = file_data["mapped"]
                            s1_local = st.session_state.get("stage1", {})
                            if "salary_gross" in mapped:
                                s1_local["salary_gross"] = mapped["salary_gross"]
                            if "taxes_tds" in mapped:
                                s1_local["taxes_paid_tds"] = mapped["taxes_tds"]
                            st.session_state["stage1"] = s1_local
                            st.success("✅ Data applied to form! Review and adjust as needed.")
                            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        s1 = st.session_state["stage1"]
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        s1["assessment_year"] = st.selectbox(
            "Assessment Year",
            ["2024-25", "2025-26"],
            index=0 if s1.get("assessment_year") == "2024-25" else 1,
        )
        s1["user_full_name"] = st.text_input("Name", value=s1.get("user_full_name", ""), key="user_name")
        s1["age"] = int(st.number_input("Age", min_value=18, max_value=100, value=int(s1.get("age", 30)), key="user_age"))
        status_options = ["Resident India", "Non Resident"]
        status_map = {"Resident India": "resident_india", "Non Resident": "non_resident"}
        reverse_map = {"resident_india": "Resident India", "non_resident": "Non Resident"}
        current_status = reverse_map.get(s1.get("residential_status", "resident_india"), "Resident India")
        selected_status = st.selectbox("Residential Status", status_options, index=status_options.index(current_status))
        s1["residential_status"] = status_map[selected_status]
        st.session_state["stage1"] = s1
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Analyze My Financial Data", type="primary", use_container_width=True, key="btn_analyze"):
            if is_user_valid():
                st.session_state["show_analyzing"] = True
                st.rerun()
            else:
                st.error("Please complete the required user details.")

    if st.session_state.get("show_analyzing"):
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">Analyzing Your Financial Data</div>', unsafe_allow_html=True)
        st.markdown('<p>Our AI is crunching the numbers to find every possible saving.</p>', unsafe_allow_html=True)
        steps = [
            "Extracting data from bank statement…",
            "Parsing Form 16 income sections…",
            "Calculating Old Tax Regime liability…",
            "Calculating New Tax Regime liability…",
            "Checking for 80C / 80D / 80GG opportunities…",
            "Generating personalized recommendations…",
        ]
        placeholder = st.empty()
        progress = st.progress(0)
        for i, line in enumerate(steps):
            placeholder.markdown(f"• {line}")
            progress.progress((i + 1) / len(steps))
            time.sleep(0.8)
        # Compute baseline recommendation before moving forward
        profile_v2 = build_taxprofile_v2(
            st.session_state.get("stage1", {}),
            st.session_state.get("stage2", {}),
            {},
            {}
        )
        status, data = api_post(api_base, "/tax/recommendation", profile_v2)
        if status == 200:
            st.session_state["last_reco"] = data
            st.session_state["current_stage"] = 2
        else:
            st.session_state["update_error"] = f"Error {status}: {data.get('detail', 'Unknown error')}"

        st.session_state["show_analyzing"] = False
        st.session_state["active_tab"] = 3
        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif active_tab == 3:
    st.markdown('<div class="ww-card">', unsafe_allow_html=True)
    st.markdown('<div class="ww-card-title">WealthWise</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top:0.2rem;">Deductions & Optimize</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("update_error"):
        st.error(f"❌ {st.session_state['update_error']}")
        del st.session_state["update_error"]

    left, right = st.columns([1, 1.3])
    with left:
        reco = st.session_state.get("last_reco")
        if reco:
            bullets = safe_get(reco, ["explanation", "bullets"], []) or []
            old_tax = safe_get(reco, ["regime", "old_tax"], 0)
            new_tax = safe_get(reco, ["regime", "new_tax"], 0)
            best_regime = safe_get(reco, ["regime", "recommended"], "OLD").upper()
            st.markdown('<div class="ww-card">', unsafe_allow_html=True)
            st.markdown('<div class="ww-card-title">💡 Key Insights</div>', unsafe_allow_html=True)
            if bullets:
                for b in bullets[:4]:
                    st.markdown(f"<div style='font-size:0.8rem;color:#E2E8F0;'>• {b}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.8rem;color:#10B981;margin-top:0.3rem;'>Better regime: {best_regime}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<div class="ww-card-title">📌 Tax-Saving Recommendations</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.8rem;">Get actionable ways to save more tax based on your profile.</p>', unsafe_allow_html=True)
        if st.button("Get Recommendations", type="primary", use_container_width=True, key="btn_get_scenarios_left"):
            profile_v2 = build_taxprofile_v2(
                st.session_state.get("stage1", {}),
                st.session_state.get("stage2", {}),
                {},
                {}
            )
            status, data = api_post(api_base, "/tax/scenarios", profile_v2)
            if status == 200:
                st.session_state["scenario_data"] = data
            else:
                st.session_state["scenario_error"] = data.get("detail", "Unknown error")

        if st.session_state.get("scenario_error"):
            st.error(f"❌ {st.session_state['scenario_error']}")
            st.session_state.pop("scenario_error", None)

        scenario_data = st.session_state.get("scenario_data")
        if scenario_data:
            st.markdown('<div style="margin-top:0.6rem;font-size:0.85rem;color:#CBD5E1;">Top Ways to Save More Tax</div>', unsafe_allow_html=True)
            for s in scenario_data.get("top_scenarios", [])[:3]:
                rec_regime = s.get("recommended_regime", "old")
                saved_key = f"tax_saved_{rec_regime}_regime"
                saved_amount = s.get(saved_key, 0)
                st.markdown(
                    f"<div style='padding:0.5rem 0;border-bottom:1px solid #334155;'>"
                    f"<div style='font-weight:600;color:#E2E8F0;'>{s.get('description')}</div>"
                    f"<div style='font-size:0.8rem;color:#CBD5E1;'>{s.get('modification','')}</div>"
                    f"<div style='font-size:0.85rem;color:#10B981;'>Saves {rupee(saved_amount)}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with st.expander("View all scenarios"):
                for s in scenario_data.get("all_applicable_scenarios", []):
                    rec_regime = s.get("recommended_regime", "old")
                    saved_key = f"tax_saved_{rec_regime}_regime"
                    saved_amount = s.get(saved_key, 0)
                    st.markdown(
                        f"<div style='padding:0.4rem 0;border-bottom:1px solid #334155;'>"
                        f"<div style='font-weight:600;color:#E2E8F0;'>{s.get('description')}</div>"
                        f"<div style='font-size:0.8rem;color:#CBD5E1;'>{s.get('modification','')}</div>"
                        f"<div style='font-size:0.85rem;color:#10B981;'>Saves {rupee(saved_amount)}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        s1 = st.session_state["stage1"]
        s2 = st.session_state["stage2"]
        st.markdown('<div class="ww-card"><div class="ww-card-title">Step 2: Deductions & Assets</div>', unsafe_allow_html=True)

        has_inv = st.checkbox("I have tax-saving investments", value=s2.get("has_investments", False), key="inv_ck")
        s2["has_investments"] = has_inv
        if has_inv:
            c1, c2 = st.columns(2)
            with c1:
                s2["deduction_80c_total"] = st.number_input("Section 80C", min_value=0.0, max_value=150000.0, value=float(s2.get("deduction_80c_total", 0.0)), step=1000.0, format="%.2f", key="ded_80c")
            with c2:
                s2["deduction_80ccd_1b_nps"] = st.number_input("NPS (80CCD 1B)", min_value=0.0, max_value=50000.0, value=float(s2.get("deduction_80ccd_1b_nps", 0.0)), step=1000.0, format="%.2f", key="ded_nps")
            s2["deduction_80d_self"] = st.number_input("Health Insurance (80D)", min_value=0.0, value=float(s2.get("deduction_80d_self", 0.0)), step=1000.0, format="%.2f", key="ded_80d")

        has_loan = st.checkbox("I have a home loan", value=s2.get("has_home_loan", False), key="loan_ck")
        s2["has_home_loan"] = has_loan
        if has_loan:
            c1, c2 = st.columns(2)
            with c1:
                s2["home_loan_interest_paid"] = st.number_input("Interest Paid (₹/year)", min_value=0.0, value=float(s2.get("home_loan_interest_paid", 0.0)), step=10000.0, format="%.2f", key="loan_int")
            with c2:
                s2["home_loan_amount"] = st.number_input("Loan Outstanding", min_value=0.0, value=float(s2.get("home_loan_amount", 0.0)), step=10000.0, format="%.2f", key="loan_amt")

        has_rental = st.checkbox("I earn rental income", value=s2.get("has_rental", False), key="rental_ck")
        s2["has_rental"] = has_rental
        if has_rental:
            c1, c2 = st.columns(2)
            with c1:
                s2["rental_income"] = st.number_input("Annual Rental (₹)", min_value=0.0, value=float(s2.get("rental_income", 0.0)), step=10000.0, format="%.2f", key="rental_inc")
            with c2:
                s2["property_count"] = st.number_input("Properties", min_value=0, value=int(s2.get("property_count", 0)), key="prop_count")

        st.session_state["stage2"] = s2
        st.session_state["stage1"] = s1

        def update_deductions_handler():
            stage1_local = st.session_state.get("stage1", {})
            stage2_local = st.session_state.get("stage2", {})
            for k, src in [
                ("salary_gross", "inp_salary"),
                ("taxes_paid_tds", "inp_tds"),
                ("age", "inp_age"),
            ]:
                if src in st.session_state:
                    stage1_local[k] = st.session_state[src]
            for k, src in [
                ("has_investments", "inv_ck"),
                ("deduction_80c_total", "ded_80c"),
                ("deduction_80ccd_1b_nps", "ded_nps"),
                ("deduction_80d_self", "ded_80d"),
                ("has_home_loan", "loan_ck"),
                ("home_loan_interest_paid", "loan_int"),
                ("home_loan_amount", "loan_amt"),
                ("has_rental", "rental_ck"),
                ("rental_income", "rental_inc"),
                ("property_count", "prop_count"),
            ]:
                if src in st.session_state:
                    stage2_local[k] = st.session_state[src]

            st.session_state["stage1"] = stage1_local
            st.session_state["stage2"] = stage2_local

            profile_v2 = build_taxprofile_v2(stage1_local, stage2_local, {}, {})
            status, data = api_post(api_base, "/tax/recommendation", profile_v2)
            if status == 200:
                st.session_state["last_reco"] = data
                st.session_state["update_success"] = True
            else:
                st.session_state["update_error"] = f"Error {status}: {data.get('detail', 'Unknown')}"

        if st.button("Update Deductions", type="primary", use_container_width=True, key="btn_update_ded", on_click=update_deductions_handler):
            pass

        if st.session_state.get("update_success"):
            st.success("✅ Deductions updated!")
            del st.session_state["update_success"]
            st.rerun()
        if st.session_state.get("update_error"):
            st.error(f"❌ {st.session_state['update_error']}")
            del st.session_state["update_error"]

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Continue to Chat & Review", type="secondary", use_container_width=True, key="btn_to_chat"):
            if is_deductions_ready():
                st.session_state["active_tab"] = 4
                st.rerun()
            else:
                st.warning("Update deductions to proceed.")

elif active_tab == 4:
    st.markdown('<div class="ww-card">', unsafe_allow_html=True)
    st.markdown('<div class="ww-card-title">WealthWise</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top:0.2rem;">Chat & Review</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="ww-card"><div class="ww-card-title">Step 3: Review & Export</div>', unsafe_allow_html=True)
        if st.session_state.get("last_reco"):
            review_summary = build_review_summary(
                st.session_state["last_reco"],
                st.session_state.get("stage1", {}),
                st.session_state.get("stage2", {}),
                st.session_state.get("scenario_data")
            )
            st.markdown(f"<div style='font-weight:600;color:#E2E8F0;margin-bottom:0.3rem;'>{review_summary['headline']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#CBD5E1;font-size:0.85rem;margin-bottom:0.5rem;'>{review_summary['summary']}</div>", unsafe_allow_html=True)

            if st.button("Generate AI Summary & Recommendations", type="secondary", use_container_width=True, key="btn_ai_summary"):
                ai_text = generate_ai_summary(review_summary, OPENROUTER_API_KEY)
                if ai_text:
                    st.session_state["review_ai_summary"] = ai_text
                else:
                    st.session_state["review_ai_summary"] = "AI summary unavailable. Showing rule-based summary above."

            if st.session_state.get("review_ai_summary"):
                st.markdown('<div style="margin-top:0.6rem;font-size:0.85rem;color:#E2E8F0;white-space:pre-wrap;">', unsafe_allow_html=True)
                st.markdown(st.session_state["review_ai_summary"])
                st.markdown('</div>', unsafe_allow_html=True)

            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                text = c.beginText(40, 750)
                text.textLine("WealthWise AI - Tax Review Summary")
                text.textLine(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                text.textLine(" ")
                text.textLine(review_summary["headline"])
                text.textLine(review_summary["summary"])
                text.textLine(" ")
                text.textLine("Key Insights:")
                for line in review_summary.get("insights", [])[:6]:
                    text.textLine(f"- {line}")
                text.textLine(" ")
                text.textLine("Future Year Pointers:")
                for line in review_summary.get("future_pointers", []):
                    text.textLine(f"- {line}")
                c.drawText(text)
                c.showPage()
                c.save()
                pdf_bytes = buffer.getvalue()
                buffer.close()

                st.download_button(
                    label="Download PDF Summary",
                    data=pdf_bytes,
                    file_name="tax_review_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception:
                st.info("Install reportlab to enable PDF export.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="ww-card"><div class="ww-card-title">ASK A TAX QUESTION</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.8rem;margin:0 0 0.6rem 0;">Ask about regimes, deductions, or eligibility.</p>', unsafe_allow_html=True)

        suggested_questions = [
            "What is the best regime for my income?",
            "How much can I save with 80C investments?",
            "Is NPS (80CCD 1B) worth it for me?",
            "How does rental income affect my tax?",
            "Can I claim home loan interest in old regime?",
            "What deductions are still unused?",
            "Do I need to file ITR-1 or ITR-2?",
            "What is my tax liability in the new regime?",
            "How can I reduce taxable income legally?",
            "What documents do I need for deductions?"
        ]

        st.markdown('<div style="margin-bottom:0.5rem;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#94A3B8;margin-bottom:0.2rem;">Suggested questions:</div>', unsafe_allow_html=True)
        for q in suggested_questions:
            st.markdown(f'<div style="font-size:0.8rem;color:#CBD5E1;">• {q}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("clear_chat_input"):
            st.session_state["chat_input"] = ""
            st.session_state["clear_chat_input"] = False

        for msg in st.session_state["chat_history"][-10:]:
            role = msg.get("role", "assistant")
            label = "You" if role == "user" else "WealthWise"
            color = "#93C5FD" if role == "user" else "#E2E8F0"
            align = "right" if role == "user" else "left"
            st.markdown(
                f'<div style="margin-bottom:0.4rem;text-align:{align};">'
                f'<div style="font-size:0.75rem;color:#94A3B8;">{label}</div>'
                f'<div style="color:{color};font-size:0.85rem;line-height:1.4;">{msg.get("content", "")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        user_q = st.text_input("", placeholder="Ask a question about your tax situation...", key="chat_input")
        if st.button("Send", type="secondary", use_container_width=True, key="btn_chat_send"):
            if user_q.strip():
                st.session_state["chat_history"].append({"role": "user", "content": user_q.strip()})
                profile_v2 = build_taxprofile_v2(
                    st.session_state.get("stage1", {}),
                    st.session_state.get("stage2", {}),
                    {},
                    {}
                )
                recent_context = st.session_state["chat_history"][-10:]
                context_text = "\n".join([f"{m['role'].title()}: {m['content']}" for m in recent_context])
                prompt = f"Conversation so far:\n{context_text}\n\nUser question: {user_q.strip()}"
                try:
                    status, data = api_post(api_base, "/tax/chat", {
                        "user_message": prompt,
                        "profile": profile_v2
                    })
                    if status == 200:
                        reply = ""
                        if "response" in data:
                            reply = data.get("response", "")
                        elif "recommendation" in data:
                            reply = data["recommendation"].get("explanation", {}).get("user_friendly", "")
                        elif "explanation" in data:
                            reply = data["explanation"].get("user_friendly", "")
                        elif "missing_info" in data:
                            missing = data.get("missing_info", {})
                            req = ", ".join(missing.get("required", []))
                            opt = ", ".join(missing.get("optional", []))
                            reply = f"Required: {req}. Optional: {opt}."
                        else:
                            reply = "I couldn't generate a response for that yet."
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                    else:
                        st.session_state["chat_history"].append({"role": "assistant", "content": f"Error: {data.get('detail', 'Unknown error')}"})
                except Exception as e:
                    st.session_state["chat_history"].append({"role": "assistant", "content": f"Error: {str(e)}"})
                st.session_state["clear_chat_input"] = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
