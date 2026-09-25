from typing import TypedDict, List, Dict, Any, Optional

class EvidenceEntry(TypedDict):
    evidence_id: str
    source_type: str
    source_ref: str
    summary: str
    raw_payload: str

class HypothesisEntry(TypedDict):
    statement: str
    status: str
    supporting_evidence_ids: List[str]

class IncidentState(TypedDict):
    incident_id: str
    title: str
    service: str
    severity: str
    raw_logs: str
    metadata: Dict[str, Any]
    evidence_ledger: List[EvidenceEntry]
    hypotheses: List[HypothesisEntry]
    root_cause: Optional[str]
    unified_diff: Optional[str]
    target_file: Optional[str]
    action_type: Optional[str]
    current_step: str
    awaiting_approval: bool
