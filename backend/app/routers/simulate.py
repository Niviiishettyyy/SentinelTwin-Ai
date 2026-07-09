import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph.twin import twin
from app.graph.simulate_engine import run_simulation
from app import schemas, models, auth

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


@router.post("", response_model=schemas.SimulationResult)
def start_simulation(payload: schemas.SimulationRequest, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    result = run_simulation(twin.graph, entry_node=payload.entry_node)

    run = models.SimulationRun(
        scenario_name=payload.scenario_name,
        status="completed",
        steps_json=json.dumps(result["steps"]),
        peak_risk=result["peak_risk"],
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return schemas.SimulationResult(
        run_id=run.id,
        scenario_name=run.scenario_name,
        status=run.status,
        steps=[schemas.SimulationStep(**s) for s in result["steps"]],
        peak_risk=result["peak_risk"],
    )


@router.get("/{run_id}", response_model=schemas.SimulationResult)
def get_simulation(run_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    run = db.query(models.SimulationRun).filter(models.SimulationRun.id == run_id).first()
    if not run:
        return schemas.SimulationResult(run_id=run_id, scenario_name="unknown", status="not_found", steps=[], peak_risk=0.0)
    steps = json.loads(run.steps_json or "[]")
    return schemas.SimulationResult(
        run_id=run.id, scenario_name=run.scenario_name, status=run.status,
        steps=[schemas.SimulationStep(**s) for s in steps], peak_risk=run.peak_risk,
    )
