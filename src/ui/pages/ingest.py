import streamlit as st
from src.ui.layout import render_header, render_tunnel_progress

def render_ingest():
    render_header("Document Collection Hub", "Upload your financial documents to activate Guardians.")
    render_tunnel_progress(1, 3)

    st.markdown(
        """
        <div style="margin-bottom: 2rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px;">
            <div style="font-weight: 600; color: #60A5FA;">ℹ️ Privacy First</div>
            <div style="font-size: 0.9rem; color: var(--text-secondary);">All documents are processed locally. No personal data leaves your device.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Grid Layout for Upload Blocks
    col1, col2 = st.columns(2)
    
    with col1:
        # SALARY BLOCK
        is_demo = st.session_state.get("demo_mode", False)
        salary_status = "✅ Uploaded" if is_demo else "Waiting..."
        salary_class = "ww-card ww-card-active" if is_demo else "ww-card"
        
        st.markdown(f'<div class="{salary_class}">', unsafe_allow_html=True)
        st.markdown('<h3>💼 SALARY (Form 16)</h3>', unsafe_allow_html=True)
        if is_demo:
             st.markdown(f'<div style="color: var(--primary); font-weight: 600; margin-bottom: 1rem;">{salary_status}</div>', unsafe_allow_html=True)
             st.markdown('<div class="text-mono" style="font-size: 0.9rem;">Detected: ₹24.5L Gross Salary</div>', unsafe_allow_html=True)
        else:
            st.file_uploader("Upload Form 16 Part B (PDF)", type=["pdf"], key="u_form16")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PORTFOLIO BLOCK
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<h3>📊 PORTFOLIO (P&L)</h3>', unsafe_allow_html=True)
        if is_demo:
             st.markdown(f'<div style="color: var(--primary); font-weight: 600; margin-bottom: 1rem;">✅ Uploaded</div>', unsafe_allow_html=True)
             st.markdown('<div class="text-mono" style="font-size: 0.9rem;">Detected: ₹1.15L LTCG</div>', unsafe_allow_html=True)
        else:
            st.file_uploader("Upload Zerodha/Groww P&L (XLSX/CSV)", type=["xlsx", "csv"], key="u_pnl")
        st.markdown('</div>', unsafe_allow_html=True)


    with col2:
        # FREELANCE/BANK BLOCK
        st.markdown('<div class="ww-card">', unsafe_allow_html=True)
        st.markdown('<h3>🔧 FREELANCE (Bank Stmt)</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.85rem; color: var(--text-secondary);">Upload bank statement to detect business expenses and income.</p>', unsafe_allow_html=True)
        
        if is_demo:
             st.markdown(f'<div style="color: var(--primary); font-weight: 600; margin-bottom: 1rem;">✅ Uploaded</div>', unsafe_allow_html=True)
             st.markdown('<div class="text-mono" style="font-size: 0.9rem;">Detected: 450+ Transactions</div>', unsafe_allow_html=True)
        else:
            st.file_uploader("Upload Bank Statement (PDF/CSV)", type=["pdf", "csv"], key="u_bank")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # WINDFALL/OTHER
        st.markdown('<div class="ww-card" style="opacity: 0.7;">', unsafe_allow_html=True)
        st.markdown('<h3>🎁 WINDFALL / RENT</h3>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Optional</div>', unsafe_allow_html=True)
        st.file_uploader("Upload Rent Receipts or Agreements", type=["pdf", "jpg"], key="u_rent")
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer Navigation
    st.markdown('<div style="margin-top: 2rem; display: flex; justify-content: flex-end;">', unsafe_allow_html=True)
    if st.button("Continue to Transaction Review →", type="primary"):
        st.session_state["current_page"] = "review"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
