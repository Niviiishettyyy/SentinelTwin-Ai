from fastapi import APIRouter, Depends
from app.graph.twin import twin
from app.graph.sweep import run_sweep
from app import auth

router = APIRouter(prefix="/api/sweep", tags=["sweep"])


@router.get("/continuous")
def continuous_sweep(current_user=Depends(auth.get_current_user)):
    return run_sweep(twin.graph)