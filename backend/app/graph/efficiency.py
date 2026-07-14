"""
Mitigation Efficiency Curve.

Answers a concrete question with evidence: if a security team only has
a fixed amount of remediation effort available (an "effort budget", in
the same normalized 0-1 operational-cost units used elsewhere in the
system), does applying mitigations in the order the recommendation
engine ranks them actually achieve more cumulative risk reduction than
a naive ordering that ignores cost-efficiency?

For each of the twin's top-N riskiest nodes, the single best-scoring
candidate action is selected (via the existing adaptive recommendation
scoring), then two orderings of "apply these actions" are simulated:
  - ranked:  by the adaptive recommendation score (what the app actually
             recommends -- balances risk reduction, cost, and history)
  - naive:   by risk_reduction alone, ignoring operational cost entirely
             (a plausible but unsophisticated real-world default: "fix
             the scariest thing first" without weighing effort)
Both orderings are walked while accumulating operational cost; once the
budget is exceeded, that ordering stops (remaining actions are treated
as unaffordable within the budget). The cumulative risk reduction at
each step is recorded for both, producing the comparison curve.
"""
from sqlalchemy.orm import Session
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes
from app.routers.recommendations import generate_recommendations


def _top_action_per_node(db: Session, top_n_nodes: int):
    risk_scores = score_all_nodes(twin.graph)
    top_nodes = sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)[:top_n_nodes]

    entries = []
    for node_id, risk in top_nodes:
        recs = generate_recommendations(db, node_id)
        if not recs:
            continue
        best = recs[0]  # already sorted by adaptive score, descending
        entries.append({
            "node": node_id,
            "node_risk": risk,
            "action": best.action,
            "risk_reduction": best.risk_reduction,
            "operational_cost": best.operational_cost,
            "adaptive_score": best.score,
        })
    return entries


def _walk_curve(entries: list, budget: float):
    cumulative_cost = 0.0
    cumulative_reduction = 0.0
    curve = []
    for e in entries:
        if cumulative_cost + e["operational_cost"] > budget:
            continue  # can't afford this one within the remaining budget
        cumulative_cost += e["operational_cost"]
        cumulative_reduction += e["risk_reduction"]
        curve.append({
            "node": e["node"],
            "action": e["action"],
            "cumulative_cost": round(cumulative_cost, 4),
            "cumulative_risk_reduction": round(cumulative_reduction, 4),
        })
    return curve


def compute_efficiency_curve(db: Session, top_n_nodes: int = 8, budget: float = 1.0):
    entries = _top_action_per_node(db, top_n_nodes)
    if not entries:
        return {"ranked_curve": [], "naive_curve": [], "budget": budget, "candidate_count": 0}

    ranked_order = sorted(entries, key=lambda e: e["adaptive_score"], reverse=True)
    naive_order = sorted(entries, key=lambda e: e["risk_reduction"], reverse=True)

    ranked_curve = _walk_curve(ranked_order, budget)
    naive_curve = _walk_curve(naive_order, budget)

    ranked_total = ranked_curve[-1]["cumulative_risk_reduction"] if ranked_curve else 0.0
    naive_total = naive_curve[-1]["cumulative_risk_reduction"] if naive_curve else 0.0

    return {
        "budget": budget,
        "candidate_count": len(entries),
        "ranked_curve": ranked_curve,
        "naive_curve": naive_curve,
        "ranked_total_reduction": ranked_total,
        "naive_total_reduction": naive_total,
        "ranked_advantage": round(ranked_total - naive_total, 4),
    }