from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.graph.calibration import submit_label, compute_calibration
from app import auth

router = APIRouter(prefix="/api/calibration", tags=["calibration"])


class LabelRequest(BaseModel):
    node_id: str
    labeler: str
    risk_rating: int  # 1-5, analyst's own blind judgment


@router.post("/label")
def submit_analyst_label(payload: LabelRequest, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    try:
        label = submit_label(db, payload.node_id, payload.labeler, payload.risk_rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"logged": True, "label_id": label.id}


@router.get("/results")
def get_calibration_results(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return compute_calibration(db)