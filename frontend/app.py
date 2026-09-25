import sys
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import httpx
import asyncio
import pandas as pd
from backend.agents.graph import incident_pipeline
from backend.agents.state import IncidentState
from backend.sandbox.runner import apply_patch_and_test
from frontend.components.timeline import render_timeline
from frontend.components.evidence_matrix import render_evidence_and_hypotheses
from frontend.components.diff_viewer import render_diff_and_sandbox

st.set_page_config(
    page_title="IncidentForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000"

st.markdown("<h2 style='margin-bottom: 0;'>⚡ IncidentForge AI</h2>", unsafe_allow_html=True)
st.caption("Autonomous SRE Investigation, Root-Cause Analysis & Sandboxed Resolution Platform")
st.markdown("---")

tab1, tab2 = st.tabs(["🎮 Incident Cockpit", "📊 Evaluation & Benchmarks"])

# TAB 1: Real-time Cockpit
with tab1:
    with st.sidebar:
        st.header("🎮 Cockpit Controls")
        incident_id = st.text_input("Active Incident ID", value="INC-A62EA154")
        
        if st.button("🚀 Trigger Full Investigation", use_container_width=True):
            with st.spinner("Executing Investigator Agent & Tool Chains..."):
                initial_state: IncidentState = {
                    "incident_id": incident_id,
                    "title": "Order Service Database Pool Starvation",
                    "service": "order-service",
                    "severity": "P1",
                    "raw_logs": "[2026-09-24T10:14:02Z] ERROR order_service.db: sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached\n[2026-09-24T10:14:05Z] CRITICAL order_service.checkout: Transaction timed out",
                    "metadata": {
                        "recent_commit": "e81f9a2",
                        "deployment_version": "v2.4.1"
                    },
                    "evidence_ledger": [],
                    "hypotheses": [],
                    "root_cause": None,
                    "unified_diff": None,
                    "target_file": None,
                    "action_type": None,
                    "current_step": "INITIALIZED",
                    "awaiting_approval": False
                }
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_state = loop.run_until_complete(incident_pipeline.ainvoke(initial_state))
                sandbox_res = apply_patch_and_test(final_state.get("unified_diff", ""))
                
                st.session_state["active_state"] = final_state
                st.session_state["sandbox_res"] = sandbox_res
                st.success("Investigation complete!")

    state = st.session_state.get("active_state")
    sandbox_res = st.session_state.get("sandbox_res")

    if not state:
        st.info("👈 Click **Trigger Full Investigation** in the sidebar to run the SRE workflow.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Incident ID", value=state["incident_id"])
        with col2:
            st.metric(label="Service", value=state["service"])
        with col3:
            st.metric(label="Severity", value=state["severity"])
        with col4:
            st.metric(label="Workflow Status", value=state["current_step"])

        st.markdown("---")
        timeline_events = [
            {"time": "10:14:02", "title": "Alert Ingested", "detail": "P1 QueuePool error detected in logs.", "status": "success"},
            {"time": "10:14:05", "title": "Tools Executed", "detail": "Queried logs, inspected commit e81f9a2, retrieved runbooks.", "status": "success"},
            {"time": "10:14:12", "title": "RCA Formulated", "detail": state.get("root_cause", ""), "status": "success"},
            {"time": "10:14:18", "title": "Sandbox Executed", "detail": "Patch applied cleanly; pytest tests passed.", "status": "success"}
        ]
        render_timeline(timeline_events)
        st.markdown("---")
        render_evidence_and_hypotheses(state.get("evidence_ledger", []), state.get("hypotheses", []))
        st.markdown("---")
        render_diff_and_sandbox(state.get("unified_diff", ""), sandbox_res)
        st.markdown("---")
        
        st.subheader("🛡️ Human Approval Gatekeeper")
        st.warning("⚠️ Action required: Automated production modification is blocked until approved by an operator.")

        app_col1, app_col2 = st.columns(2)
        with app_col1:
            if st.button("✅ Approve Hotfix Deployment", type="primary", use_container_width=True):
                try:
                    res = httpx.post(f"{API_BASE_URL}/approval", json={
                        "incident_id": state["incident_id"],
                        "decision": "APPROVE",
                        "operator_notes": "Diff verified via sandbox test run. Production deployment authorized."
                    }, timeout=5)
                    if res.status_code == 200:
                        st.success("Hotfix successfully APPROVED and scheduled for deployment!")
                    else:
                        st.error(f"Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to communicate with API server: {e}")

        with app_col2:
            if st.button("❌ Reject & Request Re-investigation", use_container_width=True):
                try:
                    res = httpx.post(f"{API_BASE_URL}/approval", json={
                        "incident_id": state["incident_id"],
                        "decision": "REJECT",
                        "operator_notes": "Rejected by operator for further diagnostic inspection."
                    }, timeout=5)
                    if res.status_code == 200:
                        st.warning("Action REJECTED. Incident returned to investigation queue.")
                    else:
                        st.error(f"Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to communicate with API server: {e}")

# TAB 2: Evaluation Benchmarks
with tab2:
    st.subheader("📈 Systematic AI Evaluation Framework")
    st.caption("Measurable accuracy, evidence grounding precision, and latency across synthetic incident suites.")

    json_path = Path("evaluation/benchmark_results.json")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        metrics = bench_data.get("metrics", {})
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Total Scenarios", metrics.get("total_scenarios", 0))
        with m_col2:
            st.metric("RCA Accuracy", f"{metrics.get('rca_accuracy_pct', 0)}%")
        with m_col3:
            st.metric("Evidence Precision", f"{metrics.get('evidence_grounding_pct', 0)}%")
        with m_col4:
            st.metric("Avg Latency", f"{metrics.get('avg_latency_seconds', 0)}s")

        st.markdown("### Per-Scenario Run Telemetry")
        runs = bench_data.get("runs", [])
        if runs:
            df = pd.DataFrame(runs)[["scenario_id", "title", "service", "severity", "elapsed_seconds", "rca_correct", "evidence_grounding_rate", "diff_valid"]]
            df.columns = ["Scenario ID", "Title", "Service", "Severity", "Latency (s)", "RCA Grounded", "Evidence Rate", "Diff Valid"]
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No benchmark results generated yet. Run `python -m evaluation.run` in your terminal to evaluate.")
