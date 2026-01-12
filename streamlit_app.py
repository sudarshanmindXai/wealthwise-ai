# streamlit_app.py
# WealthWise‑AI — Fintech-grade Streamlit UI (Forms + Chat + Presets + Polished PDF)
# ✅ No JSON shown to user (UI or chat)
# ✅ Expanded deductions UI (clean, collapsible)
# ✅ 3‑zone layout using screen space
# ✅ PDF includes customer name, NO citations content, clean alignment
# ✅ Backend unchanged (calls /tax/recommendation and /tax/chat)

from __future__ import annotations

import io
import textwrap
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

# -----------------------------
# Config
# -----------------------------
DEFAULT_API_BASE = "http://127.0.0.1:8000"
TIMEOUT_SECS = 30


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="WealthWise‑AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Fintech styling (dark, subtle)
# -----------------------------
st.markdown(
    """
<style>
.stApp { background: #0b1220; }

/* tighter, wider container */
.block-container { padding-top: 1.4rem; padding-bottom: 2.2rem; max-width: 1400px; }

/* typography */
h1,h2,h3 { color: #e5e7eb !important; letter-spacing: -0.2px; }
p,li,label,span,div { color: #cbd5e1; }
small { color: #94a3b8; }

/* sidebar */
section[data-testid="stSidebar"] {
  background: #081025;
  border-right: 1px solid rgba(148,163,184,0.12);
}
section[data-testid="stSidebar"] * { color: #cbd5e1; }

/* cards */
.ww-card {
  background: rgba(17,24,39,0.70);
  border: 1px solid rgba(148,163,184,0.14);
  border-radius: 16px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}
.ww-card-tight {
  background: rgba(17,24,39,0.70);
  border: 1px solid rgba(148,163,184,0.14);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}
.ww-subtle { color: #94a3b8; font-size: 0.92rem; }
.ww-divider { height: 1px; margin: 14px 0; background: rgba(148,163,184,0.14); }

/* badges */
.ww-badge {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  background: rgba(34,197,94,0.14); border: 1px solid rgba(34,197,94,0.22);
  color: #bbf7d0; font-size: 0.82rem;
}
.ww-badge-warn {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  background: rgba(245,158,11,0.14); border: 1px solid rgba(245,158,11,0.22);
  color: #fde68a; font-size: 0.82rem;
}
.ww-badge-muted {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  background: rgba(148,163,184,0.10); border: 1px solid rgba(148,163,184,0.18);
  color: #cbd5e1; font-size: 0.82rem;
}

/* inputs */
div[data-baseweb="select"] > div {
  background: rgba(17,24,39,0.70) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
}
input, textarea {
  background: rgba(17,24,39,0.70) !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  border-radius: 12px !important;
  color: #e5e7eb !important;
}

/* buttons */
div.stButton > button, div.stDownloadButton > button {
  background: linear-gradient(90deg, #22c55e 0%, #06b6d4 100%);
  border: 0;
  color: #06121f;
  font-weight: 750;
  border-radius: 12px;
  padding: 0.70rem 1.05rem;
}
div.stButton > button:hover, div.stDownloadButton > button:hover { filter: brightness(1.05); }

/* metric cards */
div[data-testid="stMetric"] {
  background: rgba(17,24,39,0.70);
  border: 1px solid rgba(148,163,184,0.14);
  border-radius: 16px;
  padding: 14px 14px;
}
div[data-testid="stMetric"] * { color: #e5e7eb !important; }

/* tabs */
button[data-baseweb="tab"] {
  background: rgba(17,24,39,0.60) !important;
  border: 1px solid rgba(148,163,184,0.14) !important;
  border-radius: 12px !important;
  padding: 10px 14px !important;
  color: #cbd5e1 !important;
  margin-right: 6px !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
  background: rgba(34,197,94,0.16) !important;
  border: 1px solid rgba(34,197,94,0.26) !important;
  color: #bbf7d0 !important;
}

/* expanders */
div[data-testid="stExpander"] {
  background: rgba(17,24,39,0.55);
  border: 1px solid rgba(148,163,184,0.14);
  border-radius: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Utilities
# -----------------------------
def rupee(n: Any) -> str:
    try:
        # preserve ints nicely
        if isinstance(n, float) and n.is_integer():
            n = int(n)
        return f"₹ {int(n):,}"
    except Exception:
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
    # Fast and safe check: hit /docs (GET) or root path; we avoid changing backend.
    try:
        url = f"{api_base.rstrip('/')}/docs"
        r = requests.get(url, timeout=6)
        return r.status_code in (200, 301, 302)
    except Exception:
        return False


def build_profile_from_ui(
    *,
    profile_version: str,
    assessment_year: str,
    customer_name: str,
    age: int,
    residential_status: str,
    salary_income: int,
    business_income: int,
    other_income: int,
    # deductions
    ded_80c: int,
    ded_80d: int,
    ded_80ccd_1b: int,
    ded_80tta: int,
    ded_80g: int,
    ded_other_chapter_via: int,
    # house property (optional)
    has_home_loan: bool,
    self_occupied_interest: int,
) -> Dict[str, Any]:
    # IMPORTANT: your current engine reads:
    # - income.salary (number)
    # - income.other_income (number)
    # - income.business_profession.* (optional)
    # - income.house_property.self_occupied_interest (optional)
    # - income.deductions.section_80c and others like 80d, 80ccd_1b, etc.
    profile = {
        "profile_version": profile_version,
        "assessment_year": assessment_year,
        "taxpayer": {"age": age, "residential_status": residential_status},
        "income": {
            "salary": int(salary_income),
            "other_income": int(other_income),
            "deductions": {
                "section_80c": int(ded_80c),
                "80d": int(ded_80d),
                "80ccd_1b": int(ded_80ccd_1b),
                "80tta": int(ded_80tta),
                "80g": int(ded_80g),
                "other_chapter_via": int(ded_other_chapter_via),
            },
            "business_profession": {
                # Keep shape tolerant for itr selector if it expects nested keys
                "has_business_income": bool(business_income > 0),
                "presumptive": {"opted": False},
                "non_presumptive": {"net_profit": int(business_income)},
            },
        },
        "flags": {
            "is_senior_citizen": age >= 60,
        },
    }

    if has_home_loan:
        profile["income"]["house_property"] = {
            "count_properties": 1,
            "self_occupied_interest": int(self_occupied_interest),
            "let_out_net_income": 0,
        }

    # customer_name is UI/PDF only — DO NOT send to backend
    # (We keep it separate in session_state)
    return profile


# -----------------------------
# PDF generator (polished, NO citations, includes name)
# -----------------------------
def _wrap_lines(text: str, width_chars: int) -> List[str]:
    lines: List[str] = []
    for para in (text or "").split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(para, width=width_chars))
    return lines


def generate_pdf_report(
    *,
    customer_name: str,
    profile: Dict[str, Any],
    reco: Dict[str, Any],
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Layout constants
    M = 44
    RIGHT = w - M
    y = h - 52

    def hr(ypos: float):
        c.setLineWidth(0.6)
        c.setStrokeColorRGB(0.82, 0.86, 0.92)
        c.line(M, ypos, RIGHT, ypos)

    def draw_kv(label: str, value: str, x: float, y: float):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.10, 0.12, 0.16)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.10, 0.12, 0.16)
        c.drawString(x + 140, y, value)

    def ensure_space(min_y: float):
        nonlocal y
        if y < min_y:
            c.showPage()
            y = h - 52

    # Colors
    def set_primary():
        c.setFillColorRGB(0.06, 0.10, 0.18)

    def set_muted():
        c.setFillColorRGB(0.35, 0.40, 0.48)

    # Header
    set_primary()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(M, y, "WealthWise‑AI — Tax Recommendation Report")
    y -= 18
    c.setFont("Helvetica", 10)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    set_muted()
    c.drawString(M, y, f"Generated: {now}")
    y -= 10
    if customer_name.strip():
        c.drawString(M, y, f"Customer: {customer_name.strip()}")
        y -= 10

    y -= 8
    hr(y)
    y -= 22

    # Snapshot cards (simple aligned blocks)
    ensure_space(140)
    set_primary()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(M, y, "Summary")
    y -= 16

    itr = safe_get(reco, ["itr", "recommended"], "—")
    regime = safe_get(reco, ["regime", "recommended"], "—")
    old_tax = safe_get(reco, ["regime", "old_tax"], 0)
    new_tax = safe_get(reco, ["regime", "new_tax"], 0)
    gti = safe_get(reco, ["income_breakup", "gross_total_income"], 0)
    ti_old = safe_get(reco, ["income_breakup", "taxable_income_old_regime"], 0)
    ded_old = safe_get(reco, ["income_breakup", "total_deductions_old_regime"], 0)

    set_primary()
    draw_kv("Recommended ITR:", str(itr), M, y); y -= 14
    draw_kv("Recommended Regime:", str(regime), M, y); y -= 14
    draw_kv("Gross Total Income:", rupee(gti), M, y); y -= 14
    draw_kv("Old Regime Deductions:", rupee(ded_old), M, y); y -= 14
    draw_kv("Taxable Income (Old):", rupee(ti_old), M, y); y -= 14
    draw_kv("Old Regime Tax:", rupee(old_tax), M, y); y -= 14
    draw_kv("New Regime Tax:", rupee(new_tax), M, y); y -= 18

    hr(y + 6)
    y -= 16

    # Input snapshot (aligned)
    ensure_space(160)
    c.setFont("Helvetica-Bold", 12)
    set_primary()
    c.drawString(M, y, "Inputs Used")
    y -= 16

    taxpayer = profile.get("taxpayer", {}) or {}
    income = profile.get("income", {}) or {}
    deductions = (income.get("deductions") or {}) if isinstance(income, dict) else {}

    # two-column key-values
    left_x = M
    right_x = M + 280

    def kv2(label, value):
        nonlocal y
        ensure_space(120)
        draw_kv(label, value, left_x, y)
        y -= 14

    kv2("Assessment Year:", str(profile.get("assessment_year", "—")))
    kv2("Age:", str(taxpayer.get("age", "—")))
    kv2("Residential Status:", str(taxpayer.get("residential_status", "—")))

    # right column items
    y2 = y + 42
    def draw_kv_right(label, value, yy):
        draw_kv(label, value, right_x, yy)

    draw_kv_right("Salary Income:", rupee(income.get("salary", 0)), y2); y2 -= 14
    # business income is stored under non_presumptive.net_profit
    biz = safe_get(income, ["business_profession", "non_presumptive", "net_profit"], 0)
    draw_kv_right("Business Income:", rupee(biz), y2); y2 -= 14
    draw_kv_right("Other Income:", rupee(income.get("other_income", 0)), y2); y2 -= 14

    y -= 10

    # Deductions table-ish
    ensure_space(190)
    y -= 6
    c.setFont("Helvetica-Bold", 12)
    set_primary()
    c.drawString(M, y, "Deductions (Old Regime)")
    y -= 14
    set_muted()
    c.setFont("Helvetica", 9)
    c.drawString(M, y, "Shown for completeness; actual benefit depends on eligibility and supporting details.")
    y -= 14
    set_primary()
    c.setFont("Helvetica", 10)

    ded_rows = [
        ("Section 80C", rupee(deductions.get("section_80c", 0))),
        ("Section 80D", rupee(deductions.get("80d", 0))),
        ("Section 80CCD(1B)", rupee(deductions.get("80ccd_1b", 0))),
        ("Section 80TTA", rupee(deductions.get("80tta", 0))),
        ("Section 80G", rupee(deductions.get("80g", 0))),
        ("Other Chapter VI‑A", rupee(deductions.get("other_chapter_via", 0))),
    ]

    # two-column listing
    lx, rx = M, M + 280
    for i, (k, v) in enumerate(ded_rows):
        ensure_space(120)
        if i % 2 == 0:
            draw_kv(k + ":", v, lx, y)
        else:
            draw_kv(k + ":", v, rx, y)
            y -= 14
    if len(ded_rows) % 2 == 1:
        y -= 14

    hr(y + 8)
    y -= 16

    # Explanation
    ensure_space(160)
    c.setFont("Helvetica-Bold", 12)
    set_primary()
    c.drawString(M, y, "Why this recommendation?")
    y -= 16

    bullets = safe_get(reco, ["explanation", "bullets"], []) or []
    if not isinstance(bullets, list):
        bullets = []

    # create a nicer narrative: first line highlighted, rest supporting
    set_primary()
    c.setFont("Helvetica-Bold", 10)
    primary_reason = bullets[0] if bullets else "Recommendation generated based on provided inputs."
    for line in _wrap_lines(primary_reason, 92):
        ensure_space(120)
        c.drawString(M, y, line)
        y -= 14

    supporting = bullets[1:] if len(bullets) > 1 else []
    if supporting:
        y -= 4
        set_muted()
        c.setFont("Helvetica", 10)
        for b in supporting:
            for line in _wrap_lines(f"• {b}", 100):
                ensure_space(90)
                c.drawString(M, y, line)
                y -= 13

    y -= 8
    hr(y + 8)
    y -= 18

    # Disclaimer
    ensure_space(120)
    set_primary()
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y, "Disclaimer")
    y -= 16
    set_muted()
    c.setFont("Helvetica", 9)
    disclaimer = (
        "This report is generated for informational purposes based on the inputs provided. "
        "It is not professional tax advice. Please consult a qualified tax professional "
        "for filing decisions and compliance."
    )
    for line in _wrap_lines(disclaimer, 105):
        ensure_space(70)
        c.drawString(M, y, line)
        y -= 12

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# -----------------------------
# Session state
# -----------------------------
if "form" not in st.session_state:
    st.session_state["form"] = {}

if "last_profile" not in st.session_state:
    st.session_state["last_profile"] = None

if "last_customer_name" not in st.session_state:
    st.session_state["last_customer_name"] = ""

if "last_reco" not in st.session_state:
    st.session_state["last_reco"] = None

if "chat_log" not in st.session_state:
    st.session_state["chat_log"] = []  # list of dicts: {"role": "user"/"assistant", "text": str, "meta": dict}


# -----------------------------
# Sidebar (thin, producty)
# -----------------------------
with st.sidebar:
    st.markdown("## WealthWise‑AI")
    st.markdown('<span class="ww-badge">Deterministic • Explainable</span>', unsafe_allow_html=True)
    st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

    api_base = st.text_input("FastAPI Base URL", value=DEFAULT_API_BASE)
    is_up = api_health(api_base)

    st.markdown(
        f'<span class="{ "ww-badge" if is_up else "ww-badge-warn"}">'
        f'{"Backend connected" if is_up else "Backend not running"}'
        f"</span>",
        unsafe_allow_html=True,
    )
    if not is_up:
        st.caption("Start backend: `uvicorn src.api.app:app --reload --port 8000`")

    st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Persona presets")

    preset = st.selectbox(
        "Choose a persona",
        ["Custom", "Salaried (Typical)", "Freelancer (Simple)", "High income (No deductions)"],
        index=1,
    )

    def apply_preset(p: str):
        if p == "Salaried (Typical)":
            st.session_state["form"] = {
                "profile_version": "v1",
                "assessment_year": "2024-25",
                "customer_name": "",
                "age": 30,
                "res_status": "resident",
                "salary": 1200000,
                "business": 0,
                "other": 0,
                "ded_80c": 150000,
                "ded_80d": 0,
                "ded_80ccd_1b": 0,
                "ded_80tta": 0,
                "ded_80g": 0,
                "ded_other": 0,
                "has_home_loan": False,
                "home_interest": 0,
            }
        elif p == "Freelancer (Simple)":
            st.session_state["form"] = {
                "profile_version": "v1",
                "assessment_year": "2024-25",
                "customer_name": "",
                "age": 28,
                "res_status": "resident",
                "salary": 0,
                "business": 800000,
                "other": 50000,
                "ded_80c": 50000,
                "ded_80d": 0,
                "ded_80ccd_1b": 0,
                "ded_80tta": 0,
                "ded_80g": 0,
                "ded_other": 0,
                "has_home_loan": False,
                "home_interest": 0,
            }
        elif p == "High income (No deductions)":
            st.session_state["form"] = {
                "profile_version": "v1",
                "assessment_year": "2025-26",
                "customer_name": "",
                "age": 35,
                "res_status": "resident",
                "salary": 0,
                "business": 0,
                "other": 2000000,
                "ded_80c": 0,
                "ded_80d": 0,
                "ded_80ccd_1b": 0,
                "ded_80tta": 0,
                "ded_80g": 0,
                "ded_other": 0,
                "has_home_loan": False,
                "home_interest": 0,
            }

    if st.button("Apply preset"):
        apply_preset(preset)

    st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)
    st.caption("Tip: Keep Streamlit + FastAPI running in two terminals.")


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div class="ww-card">
  <h2 style="margin:0;">Your Tax Assistant, built like a real product.</h2>
  <div class="ww-subtle">A clean workflow: profile → recommendation → explanation → export → chat.</div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

tab_reco, tab_chat = st.tabs(["📌 Recommendation", "💬 Chat"])


# -----------------------------
# Recommendation tab (3‑zone layout)
# -----------------------------
with tab_reco:
    # 3-zone: inputs | hero results | advisor rail
    left, center, right = st.columns([1.15, 1.65, 1.10], gap="large")

    # -------- Left: Inputs (clean, grouped)
    with left:
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown("### Profile")
        st.caption("Fill once — everything updates from here (no JSON anywhere).")

        f = st.session_state["form"]

        profile_version = st.text_input("Profile version", value=f.get("profile_version", "v1"))
        assessment_year = st.selectbox(
            "Assessment year",
            ["2024-25", "2025-26"],
            index=0 if f.get("assessment_year", "2024-25") == "2024-25" else 1,
        )
        customer_name = st.text_input("Customer name (for PDF)", value=f.get("customer_name", ""))

        c1, c2 = st.columns([1, 1])
        with c1:
            age = st.number_input("Age", min_value=18, max_value=100, value=int(f.get("age", 30)), step=1)
        with c2:
            res_status = st.selectbox(
                "Residential status",
                ["resident", "non_resident"],
                index=0 if f.get("res_status", "resident") == "resident" else 1,
            )

        is_senior = age >= 60
        st.markdown(
            f'<span class="{ "ww-badge-warn" if is_senior else "ww-badge-muted"}">'
            f'{"Senior citizen (60+)" if is_senior else "Non-senior"}'
            f"</span>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

        st.markdown("### Income")
        salary = st.number_input("Salary income (₹/year)", min_value=0, value=int(f.get("salary", 1200000)), step=50000)
        business = st.number_input(
            "Business / professional income (₹/year)",
            min_value=0,
            value=int(f.get("business", 0)),
            step=50000,
        )
        other = st.number_input("Other income (₹/year)", min_value=0, value=int(f.get("other", 0)), step=10000)

        st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

        st.markdown("### Deductions (Old regime)")
        st.caption("Shown for trust & completeness. Enter what applies to you.")

        with st.expander("Chapter VI‑A deductions", expanded=True):
            ded_80c = st.number_input("Section 80C (₹)", min_value=0, max_value=150000, value=int(f.get("ded_80c", 150000)), step=5000)
            ded_80d = st.number_input("Section 80D (₹)", min_value=0, value=int(f.get("ded_80d", 0)), step=5000)
            ded_80ccd_1b = st.number_input("Section 80CCD(1B) (₹)", min_value=0, value=int(f.get("ded_80ccd_1b", 0)), step=5000)
            ded_80tta = st.number_input("Section 80TTA (₹)", min_value=0, value=int(f.get("ded_80tta", 0)), step=5000)
            ded_80g = st.number_input("Section 80G (₹)", min_value=0, value=int(f.get("ded_80g", 0)), step=5000)
            ded_other = st.number_input("Other Chapter VI‑A (₹)", min_value=0, value=int(f.get("ded_other", 0)), step=5000)

        with st.expander("Home loan / House property (optional)", expanded=False):
            has_home_loan = st.checkbox("I have home loan interest (Section 24)", value=bool(f.get("has_home_loan", False)))
            home_interest = st.number_input(
                "Self‑occupied interest (₹/year)",
                min_value=0,
                value=int(f.get("home_interest", 0)),
                step=10000,
                disabled=not has_home_loan,
            )

        st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

        # Save form state continuously
        st.session_state["form"] = {
            "profile_version": profile_version,
            "assessment_year": assessment_year,
            "customer_name": customer_name,
            "age": int(age),
            "res_status": res_status,
            "salary": int(salary),
            "business": int(business),
            "other": int(other),
            "ded_80c": int(ded_80c),
            "ded_80d": int(ded_80d),
            "ded_80ccd_1b": int(ded_80ccd_1b),
            "ded_80tta": int(ded_80tta),
            "ded_80g": int(ded_80g),
            "ded_other": int(ded_other),
            "has_home_loan": bool(has_home_loan),
            "home_interest": int(home_interest),
        }

        a1, a2 = st.columns([1.25, 1.0])
        with a1:
            run_btn = st.button("Generate recommendation", type="primary", disabled=not is_up)
        with a2:
            clear_btn = st.button("Clear")

        if clear_btn:
            st.session_state["last_profile"] = None
            st.session_state["last_customer_name"] = ""
            st.session_state["last_reco"] = None

        st.markdown("</div>", unsafe_allow_html=True)

        # Run backend call
        if run_btn:
            profile = build_profile_from_ui(
                profile_version=profile_version,
                assessment_year=assessment_year,
                customer_name=customer_name,
                age=int(age),
                residential_status=res_status,
                salary_income=int(salary),
                business_income=int(business),
                other_income=int(other),
                ded_80c=int(ded_80c),
                ded_80d=int(ded_80d),
                ded_80ccd_1b=int(ded_80ccd_1b),
                ded_80tta=int(ded_80tta),
                ded_80g=int(ded_80g),
                ded_other_chapter_via=int(ded_other),
                has_home_loan=bool(has_home_loan),
                self_occupied_interest=int(home_interest),
            )
            st.session_state["last_profile"] = profile
            st.session_state["last_customer_name"] = customer_name.strip()

            try:
                with st.spinner("Computing recommendation..."):
                    status, data = api_post(api_base, "/tax/recommendation", profile)
            except requests.exceptions.ConnectionError:
                status, data = 0, {"detail": "Backend not reachable. Please start FastAPI and try again."}

            if status == 200:
                st.session_state["last_reco"] = data
            else:
                st.session_state["last_reco"] = None
                # Show error in center area (not JSON dump)
                st.session_state["last_error"] = (status, data)

    # -------- Center: Hero results
    reco = st.session_state.get("last_reco")
    last_error = st.session_state.get("last_error", None)

    with center:
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown("### Recommendation")
        st.caption("Your primary outcome — clear and confident.")

        if last_error and not reco:
            status, data = last_error
            msg = data.get("detail") if isinstance(data, dict) else str(data)
            st.error(f"Could not generate recommendation. {msg}")

        if not reco:
            st.markdown(
                '<span class="ww-badge-muted">Generate a recommendation to see results here.</span>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            itr = safe_get(reco, ["itr", "recommended"], "—")
            regime = safe_get(reco, ["regime", "recommended"], "—")
            old_tax = safe_get(reco, ["regime", "old_tax"], 0)
            new_tax = safe_get(reco, ["regime", "new_tax"], 0)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Recommended ITR", itr)
            m2.metric("Recommended Regime", regime)
            m3.metric("Old Regime Tax", rupee(old_tax))
            m4.metric("New Regime Tax", rupee(new_tax))

            st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

            # Explainability (nicer, connected)
            bullets = safe_get(reco, ["explanation", "bullets"], []) or []
            if not isinstance(bullets, list):
                bullets = []

            st.markdown("### Why this recommendation?")
            primary = bullets[0] if bullets else "Generated based on your inputs."
            st.markdown(
                f"""
<div class="ww-card-tight" style="border-left: 4px solid rgba(34,197,94,0.55);">
  <div class="ww-subtle">Primary reason</div>
  <div style="font-size:1.05rem; color:#e5e7eb; margin-top:6px;">
    {primary}
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            supporting = bullets[1:] if len(bullets) > 1 else []
            if supporting:
                st.write("")
                st.markdown('<div class="ww-card-tight">', unsafe_allow_html=True)
                st.markdown('<div class="ww-subtle">Supporting details</div>', unsafe_allow_html=True)
                st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)
                for s in supporting:
                    st.markdown(f"- {s}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # -------- Right: Advisor rail (breakdown, missing info, follow-ups, citations collapsed, PDF)
    with right:
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown("### Insights")
        st.caption("A clean panel for breakdown and next improvements.")

        if not reco:
            st.markdown('<span class="ww-badge-muted">Waiting for results…</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            ib = reco.get("income_breakup", {}) or {}
            st.markdown("**Income breakdown**")
            st.write("Gross total income:", rupee(ib.get("gross_total_income", 0)))
            st.write("Deductions (old):", rupee(ib.get("total_deductions_old_regime", 0)))
            st.write("Taxable (old):", rupee(ib.get("taxable_income_old_regime", 0)))

            st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

            # Missing info (no JSON)
            mi = reco.get("missing_info", {}) or {}
            req = mi.get("required", []) or []
            opt = mi.get("optional", []) or []

            st.markdown("**Improve this result**")
            if (not req) and (not opt):
                st.success("You’re all set — nothing important missing for this level of estimation.")
            else:
                if req:
                    st.warning("Missing required details:")
                    for item in req:
                        st.write("•", item)
                if opt:
                    st.info("Optional details that can improve accuracy:")
                    # show as “pills” using badges
                    for item in opt:
                        st.markdown(f'<span class="ww-badge-muted">{item}</span>', unsafe_allow_html=True)

            st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

            # Follow-ups (subtle)
            st.markdown("**Suggested next questions**")
            fqs = reco.get("followup_questions", []) or []
            if not fqs:
                st.write("No suggestions right now.")
            else:
                for q in fqs[:5]:
                    st.write("•", q)

            st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

            # Citations (collapsed + minimal, no big previews)
            citations = reco.get("citations", []) or []
            count = len(citations)
            with st.expander(f"Sources referenced ({count})", expanded=False):
                if not citations:
                    st.write("No sources attached.")
                else:
                    for citem in citations:
                        doc_id = citem.get("doc_id", "—")
                        file_ = citem.get("file", "—")
                        line = citem.get("line_no", "—")
                        st.write(f"• {doc_id} — {file_}:{line}")

            st.markdown('<div class="ww-divider"></div>', unsafe_allow_html=True)

            # PDF export (nicer, includes name, NO citations content)
            customer_name = (st.session_state.get("last_customer_name") or "").strip()
            profile_used = st.session_state.get("last_profile") or {}

            pdf_bytes = generate_pdf_report(
                customer_name=customer_name,
                profile=profile_used,
                reco=reco,
            )
            fname = f"wealthwise_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}Z.pdf"
            st.download_button(
                "⬇️ Export PDF report",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                type="primary",
            )

            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Chat tab (NO JSON, product chat)
# -----------------------------
with tab_chat:
    st.markdown(
        """
<div class="ww-card">
  <h3 style="margin:0;">Chat with WealthWise</h3>
  <div class="ww-subtle">Ask questions in plain English. You’ll never see raw system JSON.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.write("")

    # Chat uses current form values
    f = st.session_state.get("form", {})
    customer_name = (f.get("customer_name") or "").strip()

    chat_profile = build_profile_from_ui(
        profile_version=f.get("profile_version", "v1"),
        assessment_year=f.get("assessment_year", "2024-25"),
        customer_name=customer_name,
        age=int(f.get("age", 30)),
        residential_status=f.get("res_status", "resident"),
        salary_income=int(f.get("salary", 0)),
        business_income=int(f.get("business", 0)),
        other_income=int(f.get("other", 0)),
        ded_80c=int(f.get("ded_80c", 0)),
        ded_80d=int(f.get("ded_80d", 0)),
        ded_80ccd_1b=int(f.get("ded_80ccd_1b", 0)),
        ded_80tta=int(f.get("ded_80tta", 0)),
        ded_80g=int(f.get("ded_80g", 0)),
        ded_other_chapter_via=int(f.get("ded_other", 0)),
        has_home_loan=bool(f.get("has_home_loan", False)),
        self_occupied_interest=int(f.get("home_interest", 0)),
    )

    # Quick prompts
    qp1, qp2, qp3, qp4 = st.columns(4)
    if qp1.button("Which ITR should I file?"):
        st.session_state["chat_q"] = "Which ITR should I file?"
    if qp2.button("Old vs New regime for me?"):
        st.session_state["chat_q"] = "Old vs New regime for my profile — which is better?"
    if qp3.button("What information is missing?"):
        st.session_state["chat_q"] = "What information is missing to improve accuracy?"
    if qp4.button("How did you decide?"):
        st.session_state["chat_q"] = "Explain why you recommended this ITR and regime."

    st.write("")

    q = st.text_input(
        "Ask a question",
        value=st.session_state.get("chat_q", "Which ITR should I file?"),
        key="chat_q",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        send = st.button("Send", type="primary", disabled=not api_health(api_base))
    with c2:
        reset = st.button("Clear chat")

    if reset:
        st.session_state["chat_log"] = []

    def render_assistant_message(data: Any) -> str:
        # Convert backend response into human-friendly text ONLY.
        # Expected shapes:
        # 1) {"intent":"tax_recommendation","recommendation":{...},"disclaimer":...}
        # 2) plain string
        if isinstance(data, str):
            return data.strip()

        if not isinstance(data, dict):
            return "I received a response, but it wasn't in the expected format."

        # If router returns recommendation
        if data.get("intent") == "tax_recommendation" and isinstance(data.get("recommendation"), dict):
            r = data["recommendation"]
            itr = safe_get(r, ["itr", "recommended"], "—")
            regime = safe_get(r, ["regime", "recommended"], "—")
            old_tax = safe_get(r, ["regime", "old_tax"], 0)
            new_tax = safe_get(r, ["regime", "new_tax"], 0)

            # short, clean answer
            lines = []
            lines.append(f"Based on your current profile, you should file **{itr}**.")
            lines.append(f"The recommended tax regime is **{regime}**.")
            lines.append(f"Estimated tax: **Old {rupee(old_tax)}** vs **New {rupee(new_tax)}**.")

            # Missing info (human)
            mi = safe_get(r, ["missing_info"], {}) or {}
            opt = mi.get("optional", []) or []
            req = mi.get("required", []) or []

            if req:
                lines.append("")
                lines.append("To be confident, I need these required details:")
                for item in req:
                    lines.append(f"• {item}")

            if opt:
                lines.append("")
                lines.append("You can improve accuracy by adding (optional):")
                for item in opt[:6]:
                    lines.append(f"• {item}")

            disclaimer = data.get("disclaimer")
            if isinstance(disclaimer, str) and disclaimer.strip():
                lines.append("")
                lines.append(f"*{disclaimer.strip()}*")

            return "\n".join(lines)

        # Fallback: try common keys
        if "message" in data and isinstance(data["message"], str):
            return data["message"]

        if "detail" in data and isinstance(data["detail"], str):
            return data["detail"]

        return "I processed your request, but I couldn’t format the response cleanly. Try a different question."

    if send and q.strip():
        st.session_state["chat_log"].append({"role": "user", "text": q.strip()})

        payload = {"user_message": q.strip(), "profile": chat_profile}

        try:
            with st.spinner("Thinking..."):
                status, data = api_post(api_base, "/tax/chat", payload)
        except requests.exceptions.ConnectionError:
            status, data = 0, {"detail": "Backend not reachable. Please start FastAPI and try again."}

        if status == 200:
            pretty = render_assistant_message(data)
            st.session_state["chat_log"].append({"role": "assistant", "text": pretty})
        else:
            msg = data.get("detail") if isinstance(data, dict) else str(data)
            st.session_state["chat_log"].append({"role": "assistant", "text": f"Sorry — I couldn’t complete that. {msg}"})

    st.write("")
    st.markdown("### Conversation")

    for msg in st.session_state["chat_log"]:
        if msg["role"] == "user":
            st.markdown(
                f"""
<div class="ww-card" style="border-left: 4px solid rgba(6,182,212,0.55);">
  <div class="ww-subtle">You</div>
  <div style="font-size:1.02rem; color:#e5e7eb; margin-top:6px;">{msg["text"]}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="ww-card" style="border-left: 4px solid rgba(34,197,94,0.55);">
  <div class="ww-subtle">WealthWise</div>
  <div style="margin-top:8px; color:#e5e7eb; line-height:1.55;">
    {msg["text"].replace("\n", "<br/>")}
  </div>
</div>
""",
                unsafe_allow_html=True,
            )