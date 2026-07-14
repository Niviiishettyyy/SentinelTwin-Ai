"""
Defense Recommendation module (Section 9.5 / 9b).

Given a node (usually the top of a threat or the current point of a
simulation), generates a catalog of candidate mitigation actions and
ranks them using an adaptive UCB1 multi-armed bandit score (see
app.graph.scoring.adaptive_recommendation_score) driven by real logged
outcomes from the Experience Engine. Also lets the user log which action
they took and its outcome, closing the loop so future rankings improve.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes, adaptive_recommendation_score
from app.experience.ledger import historical_success_rate, log_incident, bandit_stats
from app import schemas, auth

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


# Candidate action catalog: (action, base_risk_reduction, operational_cost, applies_to)
# applies_to == None means it applies to any node type/exposure.
CANDIDATE_ACTIONS = [
    ("Isolate host from network", 0.75, 0.55, None),
    ("Reset compromised credentials", 0.50, 0.20, None),
    ("Patch vulnerable service", 0.55, 0.65, None),
    ("Block external IP at firewall", 0.40, 0.15, "external"),
    ("Increase monitoring / add detection rule", 0.15, 0.05, None),
]


def _pattern_for_node(node_data: dict) -> str:
    return f"{node_data.get('type', 'device')}:{node_data.get('criticality', 'low')}"


def generate_recommendations(db: Session, node_id: str):
    node_data = twin.get_node(node_id)
    if node_data is None:
        return []

    risk_scores = score_all_nodes(twin.graph)
    node_risk = risk_scores.get(node_id, 0.0)
    exposure = node_data.get("exposure", "internal")
    pattern = _pattern_for_node(node_data)

    bandit = bandit_stats(db, pattern)
    per_action_stats = bandit["per_action"]
    total_trials = bandit["total_trials"]

    recs = []
    for action, base_reduction, cost, applies_to in CANDIDATE_ACTIONS:
        if applies_to is not None and applies_to != exposure:
            continue

        # Scale the action's theoretical risk reduction by how risky the
        # node actually is right now -- a low-risk node has little to gain.
        risk_reduction = round(min(base_reduction * (0.5 + node_risk), 1.0), 4)
        hist_success = historical_success_rate(db, pattern, action)

        action_stats = per_action_stats.get(action, {"count": 0, "avg_reward": 0.5})
        score, exploration_bonus = adaptive_recommendation_score(
            risk_reduction=risk_reduction,
            operational_cost=cost,
            avg_reward=action_stats["avg_reward"] if action_stats["count"] > 0 else 0.5,
            action_trials=action_stats["count"],
            total_trials=total_trials,
        )

        trial_note = (
            f"tried {action_stats['count']}x, avg reward {action_stats['avg_reward']:.2f}"
            if action_stats["count"] > 0 else "not yet tried for this pattern"
        )

        recs.append(schemas.RecommendationOut(
            action=action,
            score=score,
            risk_reduction=risk_reduction,
            operational_cost=cost,
            historical_success=hist_success,
            rationale=(
                f"Targets node '{node_id}' (risk {node_risk:.2f}, {exposure} exposure). "
                f"Estimated risk reduction {risk_reduction:.2f} at operational cost {cost:.2f}. "
                f"Adaptive ranking: {trial_note}, exploration bonus {exploration_bonus:.3f}."
            ),
            is_adaptive=True,
            exploration_bonus=exploration_bonus,
        ))

    recs.sort(key=lambda r: r.score, reverse=True)
    return recs


@router.get("/{node_id}", response_model=list[schemas.RecommendationOut])
def get_recommendations(node_id: str, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return generate_recommendations(db, node_id)


class ApplyActionRequest(BaseModel):
    node_id: str
    action: str
    outcome: str  # contained | escalated | ineffective
    risk_reduced: float = 0.0


@router.post("/apply")
def apply_action(payload: ApplyActionRequest, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    node_data = twin.get_node(payload.node_id) or {}
    pattern = _pattern_for_node(node_data)
    incident = log_incident(db, pattern, payload.action, payload.outcome, payload.risk_reduced)
    return {"logged": True, "incident_id": incident.id}