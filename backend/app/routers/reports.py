from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes
from app import models, auth


def _business_impact(risk_scores: dict, flagged_count: int) -> dict:
    """
    Translates technical risk into rough operational-impact language
    (Section 9.8). Deliberately simple/heuristic -- refine with real
    incident cost data once available.
    """
    avg_risk = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0.0
    critical_nodes = [n for n, s in risk_scores.items() if s > 0.6]

    if avg_risk > 0.6 or len(critical_nodes) >= 3:
        level = "High"
        downtime_hours = "4-12"
    elif avg_risk > 0.35 or flagged_count > 0:
        level = "Moderate"
        downtime_hours = "1-4"
    else:
        level = "Low"
        downtime_hours = "0-1"

    return {
        "disruption_level": level,
        "estimated_recovery_hours": downtime_hours,
        "critical_assets_at_risk": critical_nodes,
    }

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/executive-summary")
def executive_summary(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    risk_scores = score_all_nodes(twin.graph)
    flagged_count = sum(1 for _, _, d in twin.all_edges() if d.get("flagged"))
    recent_runs = db.query(models.SimulationRun).order_by(models.SimulationRun.id.desc()).limit(5).all()

    return {
        "device_count": twin.graph.number_of_nodes(),
        "flagged_flows": flagged_count,
        "average_risk": round(sum(risk_scores.values()) / len(risk_scores), 4) if risk_scores else 0.0,
        "top_risk_nodes": sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)[:5],
        "business_impact": _business_impact(risk_scores, flagged_count),
        "recent_simulations": [
            {"id": r.id, "scenario": r.scenario_name, "peak_risk": r.peak_risk, "status": r.status}
            for r in recent_runs
        ],
    }
