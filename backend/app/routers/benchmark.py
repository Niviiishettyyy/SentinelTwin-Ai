"""
Exposes the Scoring Method Benchmark (app.graph.benchmark) as an API
endpoint for the frontend to display, and for the paper/report to cite
with a live, reproducible number rather than an assumed claim.
"""
from fastapi import APIRouter, Depends
from app.graph.twin import twin
from app.graph.benchmark import run_benchmark
from app import auth

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


@router.get("/scoring-methods")
def scoring_methods_benchmark(current_user=Depends(auth.get_current_user)):
    return run_benchmark(twin.graph)