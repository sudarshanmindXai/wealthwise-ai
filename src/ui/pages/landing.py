import streamlit as st
from src.utils.demo_data import load_demo_state

def render_landing():
    # Hero Section
    st.markdown(
        """
        <div style="text-align: center; padding: 4rem 1rem;">
            <h1 style="font-size: 3rem; font-weight: 800; background: linear-gradient(to right, #F8FAFC, #94A3B8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">
                Your Personal Financial Auditor
            </h1>
            <p style="font-size: 1.2rem; color: var(--text-secondary); max-width: 600px; margin: 0 auto 3rem auto;">
                WealthWise AI doesn't just calculate tax. It audits your financial life, finds leakages, and constructs a fortress around your wealth.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Primary Action
        if st.button("🚀 Start Retro-Audit", type="primary", use_container_width=True):
            st.session_state["current_page"] = "ingest"
            st.rerun()
        
        # Demo Action
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        if st.button("🧪 Try Demo (No Login)", type="secondary", use_container_width=True):
            load_demo_state(st.session_state)
            st.session_state["current_page"] = "ingest"  # Go to ingest to see pre-filled data
            st.rerun()

    # Features Grid
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 4rem;">
            <div class="ww-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
                <h3 style="font-size: 1.1rem; font-weight: 600;">Salary Sentinel</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Analyses Form 16 for missed HRA, LTA, and 80C opportunities.</p>
            </div>
            <div class="ww-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                <h3 style="font-size: 1.1rem; font-weight: 600;">Portfolio Architect</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Balances Loss Harvesting and Capital Gains to minimize tax.</p>
            </div>
            <div class="ww-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔧</div>
                <h3 style="font-size: 1.1rem; font-weight: 600;">Hustle Shield</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Protects freelance income using Section 44ADA presumptive taxation.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
