"""
ML Playground + Explainability endpoints.

/predict  -- manual feature vector -> anomaly score (no graph node needed)
/explain  -- manual feature vector -> real SHAP per-feature contributions
/status   -- whether the trained model+scaler are actually loaded
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from app.ml.predict import predict_anomaly_score, model_is_loaded, shap_explain
from app import schemas, auth

router = APIRouter(prefix="/api/ml", tags=["ml"])


class ManualPredictRequest(BaseModel):
    features: Dict[str, float]


@router.get("/status")
def ml_status(current_user=Depends(auth.get_current_user)):
    return {"model_loaded": model_is_loaded()}


@router.post("/predict")
def manual_predict(payload: ManualPredictRequest, current_user=Depends(auth.get_current_user)):
    score = predict_anomaly_score(payload.features)
    band = "critical" if score > 0.6 else "elevated" if score > 0.35 else "low"
    return {"anomaly_score": score, "risk_band": band, "model_loaded": model_is_loaded()}


@router.post("/explain", response_model=schemas.ShapExplanation)
def manual_explain(payload: ManualPredictRequest, current_user=Depends(auth.get_current_user)):
    result = shap_explain(payload.features)
    return schemas.ShapExplanation(**result)