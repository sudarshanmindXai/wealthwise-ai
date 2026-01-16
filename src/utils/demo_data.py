DEMO_PROFILE = {
    "stage1": {
        "user_full_name": "Rohan Sharma",
        "age": 32,
        "residential_status": "resident_india",
        "assessment_year": "2025-26",
        "salary_gross": 2450000.0,
        "taxes_paid_tds": 280000.0,
        "business_has_income": True,
        "business_non_presumptive_profit": 450000.0,  # Freelance
        "other_income_savings_interest": 12000.0,
        "other_income_fd_interest": 0.0,
        "other_income_dividends": 5000.0,
        "capital_gains_stcg_111a": 0.0,
        "capital_gains_ltcg_112a": 115000.0, # Portfolio LTCG
    },
    "stage2": {
        "has_investments": True,
        "deduction_80c_total": 150000.0,
        "deduction_80ccd_1b_nps": 0.0, # Opportunity
        "deduction_80d_self": 25000.0,
        "has_home_loan": False,
        "has_rental": True,
        "rental_income": 0.0, # Rent paid actually, logic handling might need tweak or this is income? Re-reading code: rental_income is INCOME. 
        # Wait, the user story mentions "Rent Paid" slider. That's for HRA/80GG. 
        # The existing code uses rental_income for 'Income from House Property'.
        # Let's stick to standard profile first.
        "property_count": 0
    },
    "transactions": [
        {
             "id": "tx_1",
             "date": "2025-01-15",
             "description": "UPI-RAZORPAY - PAYMENT RECEIVED",
             "amount": 45000.0,
             "type": "credit",
             "category_prediction": "business",
             "confidence": 0.72,
             "status": "review_needed"
        },
        {
             "id": "tx_2",
             "date": "2025-02-28",
             "description": "HDFC-NEFT-KUMAR - GIFT",
             "amount": 150000.0,
             "type": "credit",
             "category_prediction": "personal",
             "confidence": 0.45,
             "status": "review_needed"
        },
        {
            "id": "tx_3",
            "date": "2024-12-10",
            "description": "SALARY - TECH SOLUTIONS LTD",
            "amount": 185000.0,
            "type": "credit",
            "category_prediction": "salary",
            "confidence": 0.99,
            "status": "auto_classified"
        }
    ]
}

def load_demo_state(session_state):
    """
    Populates the session state with Rohan's data.
    """
    session_state["stage1"] = DEMO_PROFILE["stage1"].copy()
    session_state["stage2"] = DEMO_PROFILE["stage2"].copy()
    session_state["transactions"] = DEMO_PROFILE["transactions"][:] # simplified copy
    session_state["demo_mode"] = True
    session_state["analyzed"] = True # Skip analysis animation for demo
    session_state["last_reco"] = None # Force re-calculation
