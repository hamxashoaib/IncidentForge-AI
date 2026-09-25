import re
from typing import Dict, Any, List

BLACKLISTED_FILES = [".env", "docker-compose.yml", "Dockerfile", ".git"]

def validate_unified_diff(diff_text: str) -> Dict[str, Any]:
    """
    Statically checks a unified diff for:
    - Standard diff headers (--- and +++)
    - Hunk indicators (@@ ... @@)
    - Blacklisted/sensitive file targets
    """
    if not diff_text or not diff_text.strip():
        return {"valid": False, "error": "Diff payload is empty."}

    lines = diff_text.strip().split("\n")
    target_files: List[str] = []
    
    for line in lines:
        if line.startswith("+++ b/"):
            target_file = line.replace("+++ b/", "").strip()
            target_files.append(target_file)
            
            # Security guardrail: no touching sensitive infrastructure or secret files
            for blacklisted in BLACKLISTED_FILES:
                if blacklisted in target_file:
                    return {
                        "valid": False,
                        "error": f"Security violation: diff modifies blacklisted file '{target_file}'"
                    }

    has_diff_headers = any(l.startswith("--- ") for l in lines) and any(l.startswith("+++ ") for l in lines)
    has_hunks = any(l.startswith("@@ ") for l in lines)

    if not (has_diff_headers and has_hunks):
        return {
            "valid": False,
            "error": "Malformed patch: missing unified diff headers (--- / +++) or hunk coordinates (@@)."
        }

    return {
        "valid": True,
        "target_files": target_files,
        "line_count": len(lines)
    }
