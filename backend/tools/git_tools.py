from pathlib import Path
from typing import Dict, Any, Optional

MOCK_REPO_DIR = Path("simulator/mock_repo")

# Simulated git commit log for the mock order-service
MOCK_GIT_HISTORY = {
    "e81f9a2": {
        "commit": "e81f9a2",
        "author": "dev-ops@internal",
        "message": "perf(order-service): constrain DB pool resources on low-tier worker nodes",
        "file_changed": "order_service/config.py",
        "diff": """--- a/order_service/config.py
+++ b/order_service/config.py
@@ -3,3 +3,3 @@ class DatabaseConfig:
-    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "25"))
+    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
-    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
+    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))"""
    }
}

def inspect_recent_commits(service: str, limit: int = 3) -> Dict[str, Any]:
    """Retrieves recent commit metadata for a target service."""
    # In real mode, this executes read-only git log via GitPython or GitHub API
    commits = list(MOCK_GIT_HISTORY.values())[:limit]
    return {
        "service": service,
        "recent_commits": [
            {"commit": c["commit"], "author": c["author"], "message": c["message"]}
            for c in commits
        ]
    }

def get_commit_diff(commit_hash: str) -> Dict[str, Any]:
    """Fetches the unified git diff introduced by a specific commit."""
    commit_data = MOCK_GIT_HISTORY.get(commit_hash)
    if not commit_data:
        return {"error": f"Commit {commit_hash} not found in repository index."}
    return {
        "commit": commit_data["commit"],
        "message": commit_data["message"],
        "file_changed": commit_data["file_changed"],
        "diff": commit_data["diff"]
    }

def inspect_file(service: str, relative_path: str) -> Dict[str, Any]:
    """Reads a source file from the repository safely (read-only)."""
    target = MOCK_REPO_DIR / relative_path
    if not target.exists():
        return {"error": f"File {relative_path} does not exist."}
    
    with open(target, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "file_path": relative_path,
        "content": content
    }
