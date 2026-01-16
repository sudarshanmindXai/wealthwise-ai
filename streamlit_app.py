import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="WealthWise AI — Tax Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🛡️"
)

# Import UI modules
from src.ui.styles import apply_custom_styles, load_fonts
from src.ui.pages.landing import render_landing
from src.ui.pages.ingest import render_ingest
from src.ui.pages.review import render_review
from src.ui.pages.dashboard import render_dashboard
from src.ui.pages.report import render_report

def main():
    # Apply Design System
    load_fonts()
    apply_custom_styles()

    # Router
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "landing"

    page = st.session_state["current_page"]

    if page == "landing":
        render_landing()
    elif page == "ingest":
        render_ingest()
    elif page == "review":
        render_review()
    elif page == "dashboard":
        render_dashboard()
    elif page == "report":
        render_report()
    else:
        st.error(f"Unknown page: {page}")
        if st.button("Return to Landing"):
             st.session_state["current_page"] = "landing"
             st.rerun()

if __name__ == "__main__":
    main()
