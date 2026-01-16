import streamlit as st

def render_header(title: str, subtitle: str = ""):
    """
    Renders the consistent top bar for the application.
    """
    if st.session_state.get("demo_mode", False):
        demo_badge = '<span class="ww-badge ww-badge-info" style="margin-right: 10px;">DEMO MODE</span>'
    else:
        demo_badge = ""

    st.markdown(
        f"""
        <div class="ww-topbar" style="background: var(--surface); border-bottom: 1px solid var(--border); padding: 1rem 2rem; margin: -1rem -2rem 2rem -2rem; display: flex; align-items: center; justify-content: space-between;">
            <div style="flex: 1;">
                <h1 style="font-size: 1.5rem; margin: 0; color: var(--text-primary);">{title}</h1>
                {f'<p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0;">{subtitle}</p>' if subtitle else ''}
            </div>
            <div>
                {demo_badge}
                <span style="font-family: 'Inter', sans-serif; font-weight: 600; color: var(--text-primary);">WealthWise AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_tunnel_progress(current_step: int, total_steps: int = 3):
    """
    Renders a progress bar/stepper for the tunnel navigation.
    """
    progress = (current_step / total_steps) * 100
    st.markdown(
        f"""
        <div style="background: var(--border); height: 4px; width: 100%; border-radius: 2px; margin-bottom: 2rem;">
            <div style="background: var(--primary); height: 100%; width: {progress}%; border-radius: 2px; transition: width 0.3s ease;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
