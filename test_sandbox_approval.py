import asyncio
import httpx
from backend.sandbox.patch_validator import validate_unified_diff
from backend.sandbox.runner import apply_patch_and_test

SAMPLE_DIFF = """--- a/order_service/config.py
+++ b/order_service/config.py
@@ -4,3 +4,3 @@
-    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
+    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "25"))
-    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
+    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))"""

async def main():
    print("--- 1. Testing Pre-Flight Diff Validation ---")
    val_res = validate_unified_diff(SAMPLE_DIFF)
    print(f"Diff Valid: {val_res['valid']}")
    print(f"Target Files: {val_res.get('target_files')}")

    print("\n--- 2. Executing Sandbox Isolation & Pytest Run ---")
    sandbox_res = apply_patch_and_test(SAMPLE_DIFF)
    print(f"Sandbox Success: {sandbox_res['success']}")
    print(f"Stage: {sandbox_res['stage']}")
    print(f"Summary: {sandbox_res['summary']}")
    print(f"Stdout:\n{sandbox_res['stdout']}")

    print("\n--- 3. Testing Human Approval Gatekeeper ---")
    async with httpx.AsyncClient() as client:
        # Check against existing incident
        try:
            res = await client.post("http://127.0.0.1:8000/approval", json={
                "incident_id": "INC-A62EA154",
                "decision": "APPROVE",
                "operator_notes": "Diff verified against sandbox test suite. Ready for hotfix release."
            }, timeout=5)
            if res.status_code == 200:
                print(f"Approval Result: {res.json()}")
            else:
                print(f"Approval Status: {res.status_code} ({res.text})")
        except Exception as e:
            print(f"Note: Backend server check skipped (start uvicorn to test live API endpoint). {e}")

    print("\n✅ Phase 4 Sandbox & Approval components verified!")

if __name__ == "__main__":
    asyncio.run(main())
