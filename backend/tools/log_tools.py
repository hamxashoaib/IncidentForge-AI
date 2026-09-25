import re
from typing import Dict, Any, List

def query_service_logs(raw_logs: str, error_pattern: str = "ERROR|CRITICAL") -> Dict[str, Any]:
    """Scans incident log streams and groups matched error lines."""
    if not raw_logs:
        return {"matched_count": 0, "lines": []}
    
    lines = raw_logs.strip().split("\n")
    regex = re.compile(error_pattern, re.IGNORECASE)
    matched = [line for line in lines if regex.search(line)]
    
    return {
        "total_lines_inspected": len(lines),
        "matched_count": len(matched),
        "lines": matched
    }

def get_error_frequency(raw_logs: str) -> Dict[str, int]:
    """Counts occurrence frequency for common exception signatures."""
    if not raw_logs:
        return {}
    
    signatures = [
        "TimeoutError",
        "ConnectionRefusedError",
        "503 Service Unavailable",
        "QueuePool limit",
        "DeadlockDetected"
    ]
    
    freq = {}
    for sig in signatures:
        count = raw_logs.count(sig)
        if count > 0:
            freq[sig] = count
    return freq
