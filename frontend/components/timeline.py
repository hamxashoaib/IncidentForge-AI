import streamlit as st

def render_timeline(events: list):
    """Renders a chronological, color-coded audit trail of agent actions."""
    st.subheader("⏱️ Investigation Timeline")
    for event in events:
        icon = "🟢" if event.get("status") == "success" else "🔵"
        with st.container():
            st.markdown(
                f"""
                <div style="border-left: 3px solid #10B981; padding-left: 14px; margin-bottom: 12px;">
                    <span style="font-size: 0.85rem; color: #888;">{event.get('time', 'Just now')}</span><br>
                    <strong>{icon} {event.get('title', 'Action')}</strong>
                    <p style="margin: 4px 0 0 0; color: #ccc; font-size: 0.9rem;">{event.get('detail', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
