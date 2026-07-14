"""
Analyst Consensus Calibration.

Collects blind human risk ratings (1-5) per node -- labelers do not see
the formula's computed score while rating -- and computes Kendall's tau
rank correlation between the human-consensus ranking and the composite
formula's ranking. This is the actual validation step that turns "we
chose these weights" into "we checked these weights against independent
human judgment."
"""
from sqlalchemy.orm import Session
from scipy.stats import kendalltau
from app import models
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes


def submit_label(db: Session, node_id: str, labeler: str, risk_rating: int):
    if node_id not in twin.graph:
        raise ValueError(f"Unknown node: {node_id}")
    if not (1 <= risk_rating <= 5):
        raise ValueError("risk_rating must be between 1 and 5")
    label = models.AnalystLabel(node_id=node_id, labeler=labeler, risk_rating=risk_rating)
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


def get_consensus_ratings(db: Session) -> dict:
    """Averages all labels per node across all labelers into a single consensus score."""
    labels = db.query(models.AnalystLabel).all()
    per_node: dict = {}
    for lbl in labels:
        per_node.setdefault(lbl.node_id, []).append(lbl.risk_rating)
    return {node: round(sum(ratings) / len(ratings), 2) for node, ratings in per_node.items()}


def compute_calibration(db: Session) -> dict:
    consensus = get_consensus_ratings(db)
    if len(consensus) < 3:
        return {
            "status": "insufficient_data",
            "labeled_node_count": len(consensus),
            "minimum_required": 3,
            "message": "Need at least 3 labeled nodes to compute a meaningful rank correlation.",
        }

    formula_scores = score_all_nodes(twin.graph)
    common_nodes = [n for n in consensus if n in formula_scores]

    formula_ranks = [formula_scores[n] for n in common_nodes]
    human_ranks = [consensus[n] for n in common_nodes]

    tau, p_value = kendalltau(formula_ranks, human_ranks)

    return {
        "status": "computed",
        "labeled_node_count": len(common_nodes),
        "kendalls_tau": round(float(tau), 4) if tau == tau else 0.0,
        "p_value": round(float(p_value), 4) if p_value == p_value else 1.0,
        "per_node": [
            {"node": n, "formula_score": formula_scores[n], "human_consensus": consensus[n]}
            for n in common_nodes
        ],
    }