"""
Experience Engine (Section 9.7): Incident Ledger.

Stores prior (pattern -> action -> outcome) records. Provides two ways
to query history:
  1. historical_success_rate() -- simple success ratio, used as a cold-
     start prior when no bandit statistics exist yet.
  2. bandit_stats() -- per-action trial counts and average reward for a
     pattern, the raw inputs to the UCB1 adaptive recommendation score
     in app.graph.scoring.adaptive_recommendation_score().
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


def bandit_stats(db: Session, pattern: str) -> dict:
    """
    Per-action trial counts and average reward for a given detected
    pattern, plus the total trial count across all actions for that
    pattern. Reward is defined as the incident's logged risk_reduced
    value when outcome == 'contained', and 0.0 otherwise -- an escalated
    or ineffective action earns no reward regardless of its originally
    estimated risk reduction.
    """
    incidents = db.query(models.Incident).filter(models.Incident.detected_pattern == pattern).all()
    stats: dict = {}
    total_trials = 0
    for inc in incidents:
        reward = inc.risk_reduced if inc.outcome == "contained" else 0.0
        entry = stats.setdefault(inc.action_taken, {"count": 0, "reward_sum": 0.0})
        entry["count"] += 1
        entry["reward_sum"] += reward
        total_trials += 1
    for action, entry in stats.items():
        entry["avg_reward"] = round(entry["reward_sum"] / entry["count"], 4)
        del entry["reward_sum"]
    return {"per_action": stats, "total_trials": total_trials}