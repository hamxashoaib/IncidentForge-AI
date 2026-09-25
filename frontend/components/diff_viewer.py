import streamlit as st

def render_diff_and_sandbox(diff_text: str, sandbox_res: dict):
    """Renders the proposed unified Git diff and the isolated sandbox execution result."""
    st.subheader("🛠️ Remediation Plan & Sandbox Validation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Proposed Unified Git Diff:**")
        if diff_text:
            st.code(diff_text, language="diff")
        else:
            st.warning("No remediation patch generated.")

    with col2:
        st.markdown("**Sandbox Test Run (`pytest`):**")
        if sandbox_res:
            success = sandbox_res.get("success", False)
            if success:
                st.success(f"Status: {sandbox_res.get('summary', 'Passed')}")
            else:
                st.error(f"Status: {sandbox_res.get('summary', 'Failed')}")
            
            with st.expander("Sandbox Output & Logs", expanded=True):
                st.code(sandbox_res.get("stdout", "No output captured."), language="bash")
        else:
            st.info("Sandbox test has not run yet.")
