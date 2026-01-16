import streamlit as st
from src.ui.layout import render_header

def render_report():
    render_header("Optimization Complete", "Your WealthWise Audit Report")
    st.balloons()
    
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem;">
             <div style="font-size: 4rem;">🏆</div>
             <h2 style="font-size: 2rem; color: var(--text-primary); margin-bottom: 0.5rem;">Wealth Audit Successful</h2>
             <p style="color: var(--text-secondary);">You have successfully identified and optimized your tax structure.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Victory Stats
    col1, col2, col3 = st.columns(3)
    with col1:
         st.markdown('<div class="ww-result-main"><div class="ww-result-label">TOTAL RESCUED</div><div class="ww-result-value ww-result-value-green">₹ 14,200</div><div class="ww-result-subtext">Tax Saved</div></div>', unsafe_allow_html=True)
    with col2:
         st.markdown('<div class="ww-result-main"><div class="ww-result-label">EFFECTIVE RATE</div><div class="ww-result-value">12.4%</div><div class="ww-result-subtext">Down from 15.1%</div></div>', unsafe_allow_html=True)
    with col3:
         st.markdown('<div class="ww-result-main"><div class="ww-result-label">COMPLIANCE</div><div class="ww-result-value ww-result-value-green">100%</div><div class="ww-result-subtext">Audit Ready</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Badges
    st.markdown("### Achievements Unlocked")
    st.markdown(
        """
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
             <span class="ww-badge ww-badge-regime-old">🛡️ 44ADA Master</span>
             <span class="ww-badge ww-badge-info">⚡ Quick Auditor</span>
             <span class="ww-badge ww-badge-regime-new">📊 Loss Harvester</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Downloads
    st.markdown("### Export Reports")
    c1, c2 = st.columns(2)
    with c1:
        st.button("📄 Download Form 12BB (PDF)", use_container_width=True)
    with c2:
        st.button("💾 Export Audit JSON", use_container_width=True)

    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    if st.button("Start New Audit", type="secondary"):
        st.session_state.clear()
        st.rerun()
