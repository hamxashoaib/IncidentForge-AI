from typing import Dict, Any, List

def evaluate_root_cause(generated_rca: str, expected_keywords: List[str]) -> bool:
    """Verifies that the generated RCA statement contains expected diagnostic terms."""
    if not generated_rca:
        return False
    rca_lower = generated_rca.lower()
    # At least half of key terms must be captured
    matched = [kw for kw in expected_keywords if kw.lower() in rca_lower]
    return len(matched) >= max(1, len(expected_keywords) // 2)

def evaluate_evidence_integrity(hypotheses: List[Dict[str, Any]], evidence_ledger: List[Dict[str, Any]]) -> float:
    """
    Verifies that every cited evidence_id in hypotheses is grounded in the collected ledger.
    Returns 1.0 (100% grounded) if zero hallucinated references exist.
    """
    valid_ids = {e["evidence_id"] for e in evidence_ledger}
    total_cited = 0
    grounded_cited = 0

    for hyp in hypotheses:
        for cited_id in hyp.get("supporting_evidence_ids", []):
            total_cited += 1
            if cited_id in valid_ids:
                grounded_cited += 1

    if total_cited == 0:
        return 1.0
    return round(grounded_cited / total_cited, 2)
