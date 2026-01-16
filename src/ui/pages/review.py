import streamlit as st
from src.ui.layout import render_header, render_tunnel_progress

def render_review():
    render_header("Transaction Review", "Help us classify ambiguous transactions to maximize your savings.")
    render_tunnel_progress(2, 3)

    if "transactions" not in st.session_state:
        st.session_state["transactions"] = []

    transactions = st.session_state["transactions"]
    pending_tx = [t for t in transactions if t["status"] == "review_needed"]
    auto_tx_count = len([t for t in transactions if t["status"] == "auto_classified"])

    col_summ1, col_summ2 = st.columns(2)
    with col_summ1:
        st.markdown(f'<div style="font-size: 1.1rem; font-weight: 600; color: var(--accent);">Needs Review: {len(pending_tx)}</div>', unsafe_allow_html=True)
    with col_summ2:
        st.markdown(f'<div style="font-size: 1.1rem; color: var(--primary);">Auto-Classified: {auto_tx_count}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

    if not pending_tx:
        st.balloons()
        st.success("All transactions classified! You are ready to proceed.")
        if st.button("Go to Dashboard →", type="primary"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    # Show only the first pending transaction to focus attention (or list them all? Plan says list)
    # Plan says: "List of ambiguous items". Let's show list but make them interactive.
    
    for i, tx in enumerate(pending_tx):
        # Unique key for widgets
        tx_id = tx["id"]
        
        with st.container():
            st.markdown(
                f"""
                <div class="ww-card" style="border-left: 4px solid var(--accent);">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                             <div style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.2rem;">₹ {tx['amount']:,.2f}</div>
                             <div style="font-family: 'JetBrains Mono'; font-size: 0.9rem; color: var(--text-secondary);">{tx['date']} • {tx['description']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="background: rgba(59, 130, 246, 0.1); color: var(--accent); padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">
                                AI Guess: {tx['category_prediction'].title()} ({tx['confidence']:.0%})
                            </div>
                        </div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Action Buttons
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("🔧 Business", key=f"btn_biz_{tx_id}", help="Classify as 44ADA Business Income"):
                    tx["category"] = "business"
                    tx["status"] = "reviewed"
                    st.rerun()
            with c2:
                if st.button("👤 Personal", key=f"btn_pers_{tx_id}", help="Classify as Personal (Non-Taxable)"):
                    tx["category"] = "personal"
                    tx["status"] = "reviewed"
                    st.rerun()
            with c3:
                 if st.button("❓ Ask CA / Unsure", key=f"btn_unsure_{tx_id}"):
                     tx["status"] = "flagged"
                     st.rerun()
    
    st.markdown("---")
    st.info("💡 Tip: Classifying income as 'Business' allows you to use Section 44ADA and claim 50% flat expenses.")

    if st.button("Skip Remaining & Continue →", type="secondary"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()
