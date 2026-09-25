from typing import Dict, Any, List
from backend.agents.state import IncidentState, EvidenceEntry
from backend.tools.log_tools import query_service_logs, get_error_frequency
from backend.tools.git_tools import inspect_recent_commits, get_commit_diff, inspect_file
from backend.rag.runbook_store import search_runbooks

async def investigate_incident(state: IncidentState) -> Dict[str, Any]:
    evidence: List[EvidenceEntry] = []
    
    logs = state.get("raw_logs", "")
    log_report = query_service_logs(logs)
    freq = get_error_frequency(logs)
    
    evidence.append({
        "evidence_id": "EV-LOG-001",
        "source_type": "log_analysis",
        "source_ref": f"{state.get('service', 'unknown')}:stdout",
        "summary": f"Detected {log_report['matched_count']} critical error lines. Frequency: {freq}",
        "raw_payload": "\n".join(log_report["lines"])
    })
    
    recent_commit_hash = state.get("metadata", {}).get("recent_commit")
    if recent_commit_hash:
        diff_info = get_commit_diff(recent_commit_hash)
        evidence.append({
            "evidence_id": "EV-GIT-001",
            "source_type": "git_commit_diff",
            "source_ref": f"commit:{recent_commit_hash}",
            "summary": f"Commit by {diff_info.get('author', 'unknown')}: {diff_info.get('message', '')}",
            "raw_payload": diff_info.get("diff", "")
        })
        
        file_changed = diff_info.get("file_changed")
        if file_changed:
            current_code = inspect_file(state.get("service", ""), file_changed)
            evidence.append({
                "evidence_id": "EV-SRC-001",
                "source_type": "source_code",
                "source_ref": file_changed,
                "summary": f"Active contents of {file_changed}",
                "raw_payload": current_code.get("content", "")
            })
            
    query_topic = "QueuePool timeout connection starvation"
    runbook_results = await search_runbooks(query_topic, limit=1)
    if runbook_results:
        top = runbook_results[0]
        evidence.append({
            "evidence_id": "EV-RAG-001",
            "source_type": "runbook",
            "source_ref": top["file_source"],
            "summary": f"Runbook: {top['topic']}",
            "raw_payload": top["excerpt"]
        })

    return {
        "evidence_ledger": evidence,
        "current_step": "INVESTIGATION_COMPLETE"
    }
