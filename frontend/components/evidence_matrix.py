import streamlit as st
import pandas as pd

def render_evidence_and_hypotheses(evidence_ledger: list, hypotheses: list):
    """Renders the side-by-side factual evidence ledger vs evaluated hypotheses."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📑 Observed Evidence (Facts)")
        if not evidence_ledger:
            st.info("No evidence collected yet.")
        else:
            for item in evidence_ledger:
                with st.expander(f"[{item.get('evidence_id')}] {item.get('source_type')}"):
                    st.caption(f"Source Reference: {item.get('source_ref')}")
                    st.write(item.get("summary"))
                    st.code(item.get("raw_payload", ""), language="text")

    with col2:
        st.subheader("🧠 Hypotheses & Inferences")
        if not hypotheses:
            st.info("No hypotheses formulated yet.")
        else:
            for hyp in hypotheses:
                status = hyp.get("status", "Inconclusive")
                badge_color = "#10B981" if status == "Supported" else "#F59E0B"
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid {badge_color};">
                        <strong>Status:</strong> <span style="color: {badge_color}; font-weight: bold;">{status}</span><br>
                        <p style="margin: 6px 0 6px 0;">{hyp.get('statement')}</p>
                        <small style="color: #999;">Supporting Evidence: {', '.join(hyp.get('supporting_evidence_ids', []))}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
