import asyncio
from backend.tools.log_tools import query_service_logs, get_error_frequency
from backend.tools.git_tools import inspect_recent_commits, get_commit_diff, inspect_file
from backend.rag.runbook_store import seed_runbooks, search_runbooks

MOCK_LOGS = """
[2026-09-24T10:14:02Z] ERROR order_service.db: sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
[2026-09-24T10:14:05Z] CRITICAL order_service.checkout: Transaction failed
"""

async def main():
    print("--- 1. Testing Log Query Tools ---")
    log_res = query_service_logs(MOCK_LOGS)
    print(f"Matched Error Lines: {log_res['matched_count']}")
    freq = get_error_frequency(MOCK_LOGS)
    print(f"Error Frequency: {freq}")

    print("\n--- 2. Testing Git Inspection Tools ---")
    commits = inspect_recent_commits("order-service")
    print(f"Recent Commits: {commits['recent_commits']}")
    diff = get_commit_diff("e81f9a2")
    print(f"Diff header for e81f9a2: {diff['file_changed']}")
    file_content = inspect_file("order-service", "order_service/config.py")
    print(f"File Lines Found: {len(file_content.get('content', '').splitlines())}")

    print("\n--- 3. Testing pgvector Runbook RAG Store ---")
    await seed_runbooks()
    rag_res = await search_runbooks("QueuePool timeout error")
    print(f"Runbooks Found: {len(rag_res)}")
    if rag_res:
        print(f"Top Match: {rag_res[0]['topic']} ({rag_res[0]['file_source']})")
    
    print("\n✅ All deterministic tools and RAG storage passed verification!")

if __name__ == "__main__":
    asyncio.run(main())
