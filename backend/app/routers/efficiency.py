from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.graph.efficiency import compute_efficiency_curve
from app import auth

router = APIRouter(prefix="/api/efficiency", tags=["efficiency"])


@router.get("/mitigation-curve")
def mitigation_efficiency_curve(
    top_n_nodes: int = Query(8, ge=1, le=20),
    budget: float = Query(1.0, ge=0.0, le=10.0),
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    return compute_efficiency_curve(db, top_n_nodes=top_n_nodes, budget=budget)