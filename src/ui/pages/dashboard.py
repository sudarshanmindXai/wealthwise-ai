import streamlit as st
from src.ui.layout import render_header

def render_dashboard():
    render_header("Financial Cockpit", "The Twin-Engine Tax Simulator")
    
    # Retrieve data from state
    s1 = st.session_state.get("stage1", {})
    s2 = st.session_state.get("stage2", {})
    
    # Top Metrics
    gross_income = s1.get("salary_gross", 0) + s1.get("business_non_presumptive_profit", 0) + s1.get("capital_gains_ltcg_112a", 0)
    
    # Layout: Twin Engine
    left_engine, right_engine = st.columns([1, 1.2])
    
    with left_engine:
        st.markdown('<div style="background: var(--surface); padding: 1rem; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 1rem;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">The Past (Actuals)</h3>', unsafe_allow_html=True)
        
        st.markdown(f'<div style="font-size: 2rem; font-weight: 700; font-family: \'JetBrains Mono\';">₹ {gross_income:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: var(--text-secondary);">Total Identified Income</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Guardian Status List
        guardians = [
            {"name": "Salary Sentinel", "status": "Optimized", "icon": "🛡️", "color": "var(--primary)"},
            {"name": "Hustle Shield (44ADA)", "status": "Active", "icon": "🔧", "color": "var(--primary)"},
            {"name": "Portfolio Architect", "status": "Harvesting Done", "icon": "📊", "color": "var(--primary)"},
            {"name": "Windfall Warden", "status": "Scanning...", "icon": "🎁", "color": "var(--accent)"},
        ]
        
        for g in guardians:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem; padding: 0.5rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                    <div style="font-size: 1.2rem; margin-right: 0.8rem;">{g['icon']}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 0.9rem;">{g['name']}</div>
                        <div style="font-size: 0.8rem; color: {g['color']};">{g['status']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with right_engine:
        st.markdown('<div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; border: 1px solid var(--accent); box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: var(--accent); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">The Future (Simulation)</h3>', unsafe_allow_html=True)
        
        # Simulated Tax Calc (Simplified logic for UI demo)
        # In real implementation this would call the tax engine
        
        # Interactive Slider
        rent_paid = st.slider("Monthly Rent Paid (HRA Optimization)", 0, 50000, 15000, step=1000)
        
        # Fake calculation for visual effect
        hra_exemption = min(rent_paid * 12, gross_income * 0.1) # dummy logic
        taxable_income = gross_income - 150000 - hra_exemption # 80C
        
        old_tax_approx = taxable_income * 0.3 # very rough
        new_tax_approx = taxable_income * 0.25 # very rough
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size: 0.8rem; color: var(--text-secondary);">Old Regime Liability</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.4rem; font-weight: 700; color: #EF4444;" class="fiscal-num">₹ {old_tax_approx:,.0f}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div style="font-size: 0.8rem; color: var(--text-secondary);">New Regime Liability</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.4rem; font-weight: 700; color: #10B981;" class="fiscal-num">₹ {new_tax_approx:,.0f}</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        savings = old_tax_approx - new_tax_approx
        if savings > 0: 
            save_text = f"You save ₹ {savings:,.0f} with New Regime"
            color = "#10B981" 
        else: 
            save_text = f"Old Regime is better by ₹ {-savings:,.0f}"
            color = "#3B82F6"

        st.markdown(f'<div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; text-align: center; color: {color}; font-weight: 700; font-size: 1.1rem;">{save_text}</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        if st.button("Generate Final Report & File ->", type="primary", use_container_width=True):
             st.session_state["current_page"] = "report"
             st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
