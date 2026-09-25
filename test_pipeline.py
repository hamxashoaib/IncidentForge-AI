import asyncio
from backend.agents.graph import incident_pipeline
from backend.agents.state import IncidentState

SIMULATED_STATE: IncidentState = {
    "incident_id": "INC-A62EA154",
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

async def main():
    print("🚀 Starting LangGraph Incident Investigation Pipeline...")
    final_state = await incident_pipeline.ainvoke(SIMULATED_STATE)
    
    print("\n--- 1. Evidence Ledger Collected ---")
    for ev in final_state["evidence_ledger"]:
        print(f"[{ev['evidence_id']}] ({ev['source_type']}) -> {ev['summary']}")
        
    print("\n--- 2. Competing Hypotheses Evaluated ---")
    for hyp in final_state["hypotheses"]:
        print(f"Status: {hyp['status']} | Claim: {hyp['statement']}")
        print(f"        Supporting Evidence: {hyp['supporting_evidence_ids']}")
        
    print("\n--- 3. Root Cause Analysis ---")
    print(f"Root Cause: {final_state['root_cause']}")
    
    print("\n--- 4. Generated Patch (Unified Git Diff) ---")
    print(final_state["unified_diff"])
    
    print(f"\nWorkflow Status: {final_state['current_step']} | Awaiting Approval: {final_state['awaiting_approval']}")
    print("\n✅ LangGraph orchestration test executed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
