import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* ========== WEALTHWISE DESIGN SYSTEM ========== */
        /* COLORS & VARIABLES */
        :root {
            --background: #0F172A;
            --surface: #1E293B;
            --primary: #10B981;
            --primary-hover: #059669;
            --danger: #EF4444;
            --accent: #3B82F6;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --border: #334155;
        }

        /* GLOBAL RESET & FONTS */
        .stApp {
            background-color: var(--background);
            color: var(--text-primary);
            font-family: 'Roboto', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.02em !important;
        }

        code, pre, .stCodeBlock, .fiscal-num {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* BUTTONS */
        div.stButton > button[kind="primary"] {
            background-color: var(--primary) !important;
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: var(--primary-hover) !important;
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
            transform: translateY(-1px);
        }

        div.stButton > button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid var(--border) !important;
            color: var(--text-secondary) !important;
            border-radius: 8px;
        }
        div.stButton > button[kind="secondary"]:hover {
            border-color: var(--text-primary) !important;
            color: var(--text-primary) !important;
            background-color: var(--surface) !important;
        }

        /* CARDS (GUARDIAN CONTAINERS) */
        .ww-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        .ww-card-active {
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
        }
        .ww-card-danger {
            border-left: 4px solid var(--danger);
        }

        /* INPUTS */
        input, textarea, select, .stSelectbox > div > div {
            background-color: var(--surface) !important;
            color: var(--text-primary) !important;
            border-color: var(--border) !important;
            border-radius: 6px;
        }
        
        /* HIDE DEFAULT STREAMLIT DISRUPTIONS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* CUSTOM UTILITIES */
        .text-mono { font-family: 'JetBrains Mono', monospace; }
        .text-green { color: var(--primary); }
        .text-red { color: var(--danger); }
        .text-blue { color: var(--accent); }
        
        </style>
        """,
        unsafe_allow_html=True
    )

def load_fonts():
    # Preconnect and load Google Fonts
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True
    )
