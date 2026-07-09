from app.graph.twin import twin

def department_risk_summary(risk_scores):
    summary = {}
    for node_id in twin.graph.nodes:
        data = twin.get_node(node_id) or {}
        dept = data.get("department", "unknown")
        summary.setdefault(dept, []).append(risk_scores[node_id])
    avg_by_dept = {
        dept: sum(scores) / len(scores)
        for dept, scores in summary.items()
        if scores
    }
    return avg_by_dept

def impacted_if_down(node_id):
    direct = twin.neighbors(node_id)
    indirect = []
    for n in direct:
        indirect.extend(twin.neighbors(n))
    return {"direct": direct, "indirect": indirect}

def attack_paths_summary(risk_scores):
    flagged = [(s, t, d) for s, t, d in twin.all_edges() if d.get("flagged")]
    # Sort by destination risk so we see the most dangerous end points first
    ranked = sorted(flagged, key=lambda e: risk_scores.get(e[1], 0.0), reverse=True)
    return ranked