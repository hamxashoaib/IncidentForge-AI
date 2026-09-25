import json
import httpx
import asyncio
from pathlib import Path

SCENARIOS_DIR = Path(__file__).parent / "scenarios"

async def trigger_scenario(scenario_filename: str, api_url: str = "http://127.0.0.1:8000"):
    filepath = SCENARIOS_DIR / scenario_filename
    if not filepath.exists():
        print(f"Error: {scenario_filename} not found.")
        return

    # Using utf-8-sig automatically strips any Windows PowerShell BOM header
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    payload = {
        "title": data["title"],
        "service": data["service"],
        "severity": data["severity"],
        "error_rate": data["error_rate"],
        "raw_logs": data["raw_logs"],
        "metadata_payload": data["metadata_payload"]
    }

    print(f"🚀 Injecting simulated incident: {data['title']}...")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{api_url}/incidents", json=payload, timeout=10)
            if res.status_code == 200:
                incident = res.json()
                print("✅ Ingested successfully into PostgreSQL!")
                print(f"🆔 Incident ID: {incident['id']}")
                print(f"🔥 Severity:    {incident['severity']}")
                print(f"📊 Error Rate:  {incident['error_rate'] * 100}%")
            else:
                print(f"❌ Server returned error ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("Make sure the FastAPI server is running on http://127.0.0.1:8000")

if __name__ == "__main__":
    asyncio.run(trigger_scenario("scn_01_db_pool_exhaustion.json"))
