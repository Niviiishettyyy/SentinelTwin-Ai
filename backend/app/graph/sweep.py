"""
Continuous Attack Sweep.

Instead of picking one scenario at a time, this runs the attack
simulation engine from EVERY viable entry point in the twin (every node
with outgoing edges), not just external-facing ones -- modeling both
outside attackers and compromised insiders/already-infected devices.
Results are aggregated across all runs into a "patch priority" ranking:
which nodes get compromised most often, and at what average risk, across
many different possible attack starting points.
"""
from app.graph.simulate_engine import run_simulation


def run_sweep(graph, max_steps_per_run: int = 8):
    entry_candidates = [n for n in graph.nodes if graph.out_degree(n) > 0]
    if not entry_candidates:
        return {"runs": 0, "patch_priority": [], "entry_points_tested": []}

    compromise_counts: dict = {}
    compromise_risk_sums: dict = {}
    run_summaries = []

    for entry in entry_candidates:
        result = run_simulation(graph, entry_node=entry, max_steps=max_steps_per_run)
        for step in result["steps"]:
            node = step["node"]
            compromise_counts[node] = compromise_counts.get(node, 0) + 1
            compromise_risk_sums[node] = compromise_risk_sums.get(node, 0.0) + step["risk_delta"]
        run_summaries.append({
            "entry_point": entry,
            "steps_reached": len(result["steps"]),
            "peak_risk": result["peak_risk"],
            "final_node": result["steps"][-1]["node"] if result["steps"] else None,
        })

    total_runs = len(entry_candidates)
    patch_priority = []
    for node, count in compromise_counts.items():
        avg_risk = round(compromise_risk_sums[node] / count, 4)
        exposure_rate = round(count / total_runs, 4)
        patch_priority.append({
            "node": node,
            "times_compromised": count,
            "exposure_rate": exposure_rate,
            "average_risk_when_compromised": avg_risk,
            "priority_score": round(exposure_rate * avg_risk, 4),
        })
    patch_priority.sort(key=lambda p: p["priority_score"], reverse=True)

    return {
        "runs": total_runs,
        "entry_points_tested": entry_candidates,
        "patch_priority": patch_priority,
        "run_summaries": run_summaries,
    }