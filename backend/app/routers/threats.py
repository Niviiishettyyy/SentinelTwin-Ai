from fastapi import APIRouter, Depends
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes
from app import schemas, auth

router = APIRouter(prefix="/api/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatOut])
def list_threats(current_user=Depends(auth.get_current_user)):
    risk_scores = score_all_nodes(twin.graph)
    flagged_edges = [(s, t, d) for s, t, d in twin.all_edges() if d.get("flagged")]

    threats = []
    for i, (s, t, d) in enumerate(flagged_edges):
        path = [s, t]
        threats.append(schemas.ThreatOut(
            id=f"threat-{i+1}",
            title=f"Suspicious flow {s} -> {t}",
            probability=min(0.5 + d.get("weight", 1.0) / 10, 0.99),
            risk_score=risk_scores.get(t, 0.0),
            path=path,
            affected_assets=[t],
            evidence=[
                f"Flow flagged on port {d.get('port', 'n/a')} over {d.get('protocol', 'tcp')}",
                f"Destination node risk score: {risk_scores.get(t, 0.0):.2f}",
            ],
        ))
    threats.sort(key=lambda x: x.risk_score, reverse=True)
    return threats
