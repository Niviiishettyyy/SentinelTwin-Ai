"""
Experience Engine (Section 9.7): Incident Ledger.

Stores prior (pattern -> action -> outcome) records and looks up the
historical success rate of an action for a similar detected pattern, used
to weight the Defense Recommendation ranking (historical_success term in
Section 9b).
"""
from sqlalchemy.orm import Session
from app import models


def log_incident(db: Session, pattern: str, action: str, outcome: str, risk_reduced: float):
    incident = models.Incident(
        detected_pattern=pattern,
        action_taken=action,
        outcome=outcome,
        risk_reduced=risk_reduced,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def historical_success_rate(db: Session, pattern: str, action: str) -> float:
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.detected_pattern == pattern, models.Incident.action_taken == action)
        .all()
    )
    if not incidents:
        return 0.5  # neutral prior when there's no history yet
    successes = sum(1 for i in incidents if i.outcome == "contained")
    return round(successes / len(incidents), 4)
