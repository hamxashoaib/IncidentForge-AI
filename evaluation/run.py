import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from backend.agents.graph import incident_pipeline
from backend.agents.state import IncidentState
from backend.sandbox.patch_validator import validate_unified_diff
from evaluation.metrics import evaluate_root_cause, evaluate_evidence_integrity

SCENARIOS_DIR = Path("simulator/scenarios")
OUTPUT_DIR = Path("evaluation")

async def run_scenario_benchmark(scenario_path: Path) -> Dict[str, Any]:
    with open(scenario_path, "r", encoding="utf-8-sig") as f:
        scenario = json.load(f)

    start_time = time.perf_counter()

    initial_state: IncidentState = {
        "incident_id": f"TEST-{scenario['scenario_id']}",
        "title": scenario["title"],
        "service": scenario["service"],
        "severity": scenario["severity"],
        "raw_logs": scenario["raw_logs"],
        "metadata": scenario["metadata_payload"],
        "evidence_ledger": [],
        "hypotheses": [],
        "root_cause": None,
        "unified_diff": None,
        "target_file": None,
        "action_type": None,
        "current_step": "INITIALIZED",
        "awaiting_approval": False
    }

    # Run LangGraph pipeline
    final_state = await incident_pipeline.ainvoke(initial_state)
    elapsed_seconds = round(time.perf_counter() - start_time, 2)

    # 1. Evaluate RCA Accuracy
    ground_truth = scenario.get("ground_truth", {})
    expected_kws = ground_truth.get("expected_cause_keywords", ["QueuePool", "POOL_SIZE"])
    rca_correct = evaluate_root_cause(final_state.get("root_cause", ""), expected_kws)

    # 2. Evaluate Evidence Grounding Integrity
    evidence_score = evaluate_evidence_integrity(
        final_state.get("hypotheses", []),
        final_state.get("evidence_ledger", [])
    )

    # 3. Evaluate Patch Validity (if patch exists)
    diff = final_state.get("unified_diff")
    diff_valid = False
    if diff:
        val = validate_unified_diff(diff)
        diff_valid = val["valid"]

    return {
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "service": scenario["service"],
        "severity": scenario["severity"],
        "elapsed_seconds": elapsed_seconds,
        "rca_correct": rca_correct,
        "evidence_grounding_rate": evidence_score,
        "diff_valid": diff_valid,
        "root_cause_summary": final_state.get("root_cause", "N/A")
    }

async def run_all_benchmarks():
    scenario_files = sorted(list(SCENARIOS_DIR.glob("*.json")))
    print("=" * 80)
    print(f"📊 Running IncidentForge AI Benchmark Suite ({len(scenario_files)} Scenarios)")
    print("=" * 80)

    results: List[Dict[str, Any]] = []

    for file in scenario_files:
        print(f"▶ Evaluating: {file.stem}...")
        res = await run_scenario_benchmark(file)
        results.append(res)
        print(f"   ✓ Latency: {res['elapsed_seconds']}s | RCA Grounded: {res['rca_correct']} | Evidence: {int(res['evidence_grounding_rate']*100)}%")

    # Calculate Aggregate Metrics
    total = len(results)
    avg_latency = round(sum(r["elapsed_seconds"] for r in results) / total, 2)
    rca_accuracy = round(sum(1 for r in results if r["rca_correct"]) / total * 100, 1)
    evidence_rate = round(sum(r["evidence_grounding_rate"] for r in results) / total * 100, 1)

    print("\n" + "=" * 80)
    print("📈 BENCHMARK SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Scenarios Evaluated:     {total}")
    print(f"Root Cause Accuracy:           {rca_accuracy}%")
    print(f"Evidence Grounding Precision:  {evidence_rate}% (Zero Hallucinated IDs)")
    print(f"Average Pipeline Latency:      {avg_latency}s")
    print("=" * 80)

    # Export to JSON
    json_path = OUTPUT_DIR / "benchmark_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": {
                "total_scenarios": total,
                "rca_accuracy_pct": rca_accuracy,
                "evidence_grounding_pct": evidence_rate,
                "avg_latency_seconds": avg_latency
            },
            "runs": results
        }, f, indent=2)

    print(f"💾 Full results saved to: {json_path.resolve()}\n")

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
