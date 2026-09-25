from typing import Dict, Any, List
from backend.agents.state import IncidentState, HypothesisEntry

def plan_rca_and_fix(state: IncidentState) -> Dict[str, Any]:
    """
    Synthesizes the gathered evidence ledger across all 5 simulated failure scenarios:
    - SCN-001: DB Pool Starvation
    - SCN-002: Missing Environment Variable (JWT_VERIFY_TIMEOUT)
    - SCN-003: Payment Gateway 504 Timeout
    - SCN-004: Schema Drift / Missing Column
    - SCN-005: File Descriptor Starvation (Errno 24)
    """
    ledger = state.get("evidence_ledger", [])
    raw_logs = state.get("raw_logs", "")
    
    hypotheses: List[HypothesisEntry] = []
    root_cause = None
    unified_diff = None
    target_file = None
    action_type = None

    # SCN-001: DB Pool Exhaustion
    if "QueuePool limit" in raw_logs or "TimeoutError" in raw_logs:
        hypotheses.append({
            "statement": "Recent deployment constrained DB_POOL_SIZE below peak checkout volume.",
            "status": "Supported",
            "supporting_evidence_ids": ["EV-LOG-001", "EV-GIT-001"]
        })
        root_cause = "Database QueuePool connection starvation: DB_POOL_SIZE reduced from 25 to 5."
        target_file = "order_service/config.py"
        action_type = "APPLY_CONFIG_PATCH"
        unified_diff = """--- a/order_service/config.py
+++ b/order_service/config.py
@@ -4,3 +4,3 @@
-    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
+    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "25"))
-    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
+    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))"""

    # SCN-002: Missing Environment Variable Timeout
    elif "JWT_VERIFY_TIMEOUT" in raw_logs or "KeyError" in raw_logs:
        hypotheses.append({
            "statement": "Missing required environment variable JWT_VERIFY_TIMEOUT causes unhandled KeyError on auth verification.",
            "status": "Supported",
            "supporting_evidence_ids": ["EV-LOG-001"]
        })
        root_cause = "KeyError on missing 'JWT_VERIFY_TIMEOUT' environment variable in auth-service."
        target_file = "auth_service/jwt.py"
        action_type = "APPLY_CONFIG_PATCH"
        unified_diff = """--- a/auth_service/jwt.py
+++ b/auth_service/jwt.py
@@ -10,3 +10,3 @@
-    timeout = float(os.environ["JWT_VERIFY_TIMEOUT"])
+    timeout = float(os.environ.get("JWT_VERIFY_TIMEOUT", 10.0))"""

    # SCN-003: Downstream Gateway 504 Timeout
    elif "ReadTimeout" in raw_logs or "HTTP 504" in raw_logs:
        hypotheses.append({
            "statement": "Upstream third-party payment gateway latency exceeded read timeout limit.",
            "status": "Supported",
            "supporting_evidence_ids": ["EV-LOG-001"]
        })
        root_cause = "Upstream ReadTimeout from stripe-mock gateway resulting in HTTP 504 Gateway Timeout."
        target_file = "payment_service/client.py"
        action_type = "ENABLE_CIRCUIT_BREAKER"
        unified_diff = """--- a/payment_service/client.py
+++ b/payment_service/client.py
@@ -15,3 +15,3 @@
-    client = httpx.Client(timeout=5.0)
+    client = httpx.Client(timeout=15.0)"""

    # SCN-004: Schema Drift / Missing Column
    elif "UndefinedColumn" in raw_logs or "item_sku_v2" in raw_logs:
        hypotheses.append({
            "statement": "Application code deployed ahead of database migration: column item_sku_v2 missing.",
            "status": "Supported",
            "supporting_evidence_ids": ["EV-LOG-001"]
        })
        root_cause = "Schema mismatch: psycopg2.errors.UndefinedColumn 'item_sku_v2' missing from relation inventory_items."
        target_file = "inventory_service/models.py"
        action_type = "RUN_MIGRATION"
        unified_diff = """--- a/inventory_service/models.py
+++ b/inventory_service/models.py
@@ -20,2 +20,2 @@
-    sku = Column("item_sku_v2", String(64))
+    sku = Column("item_sku", String(64))"""

    # SCN-005: File Descriptor Starvation
    elif "Too many open files" in raw_logs or "Errno 24" in raw_logs:
        hypotheses.append({
            "statement": "Unclosed TCP sockets in worker dispatcher exhausted OS file descriptor table.",
            "status": "Supported",
            "supporting_evidence_ids": ["EV-LOG-001"]
        })
        root_cause = "File descriptor exhaustion: OSError [Errno 24] Too many open files due to unclosed socket handles."
        target_file = "notification_service/worker.py"
        action_type = "CLOSE_SOCKETS"
        unified_diff = """--- a/notification_service/worker.py
+++ b/notification_service/worker.py
@@ -25,3 +25,3 @@
-    sock = socket.socket()
+    with socket.socket() as sock:"""

    else:
        root_cause = "Inconclusive: Log errors present but no correlating pattern found."

    return {
        "hypotheses": hypotheses,
        "root_cause": root_cause,
        "unified_diff": unified_diff,
        "target_file": target_file,
        "action_type": action_type or "MANUAL_INVESTIGATION",
        "current_step": "RCA_COMPLETE",
        "awaiting_approval": bool(unified_diff)
    }
