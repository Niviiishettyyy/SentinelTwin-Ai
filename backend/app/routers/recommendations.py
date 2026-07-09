"""
Defense Recommendation module (Section 9.5 / 9b).

Given a node (usually the top of a threat or the current point of a
simulation), generates a catalog of candidate mitigation actions, scores
each with the recommendation_score formula, and ranks them. Also lets the
user log which action they took and its outcome, closing the loop into
the Experience Engine (Section 9.7) so future rankings improve.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes, recommendation_score
from app.experience.ledger import historical_success_rate, log_incident
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

    recs = []
    for action, base_reduction, cost, applies_to in CANDIDATE_ACTIONS:
        if applies_to is not None and applies_to != exposure:
            continue

        # Scale the action's theoretical risk reduction by how risky the
        # node actually is right now -- a low-risk node has little to gain.
        risk_reduction = round(min(base_reduction * (0.5 + node_risk), 1.0), 4)
        hist_success = historical_success_rate(db, pattern, action)
        score = recommendation_score(risk_reduction, cost, hist_success)

        recs.append(schemas.RecommendationOut(
            action=action,
            score=score,
            risk_reduction=risk_reduction,
            operational_cost=cost,
            historical_success=hist_success,
            rationale=(
                f"Targets node '{node_id}' (risk {node_risk:.2f}, {exposure} exposure). "
                f"Estimated risk reduction {risk_reduction:.2f} at operational cost {cost:.2f}; "
                f"historically succeeded in {hist_success * 100:.0f}% of similar past incidents."
            ),
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
