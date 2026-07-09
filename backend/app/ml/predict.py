import os
import numpy as np
import joblib

MODEL_PATH = os.environ.get("MODEL_PATH", "network_rf_model_final.pkl")
SCALER_PATH = os.environ.get("SCALER_PATH", "network_scaler_final.pkl")

_model = None
_scaler = None
_feature_order = None


def _load():
    global _model, _scaler, _feature_order
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
    if _scaler is None and os.path.exists(SCALER_PATH):
        _scaler = joblib.load(SCALER_PATH)
        _feature_order = list(getattr(_scaler, "feature_names_in_", []))
    return _model, _scaler, _feature_order


def model_is_loaded() -> bool:
    model, scaler, _ = _load()
    return model is not None and scaler is not None


def _stub_score(features: dict) -> float:
    return round(min(sum(abs(v) for v in features.values()) % 1.0, 1.0), 4)


def predict_anomaly_score(features: dict) -> float:
    model, scaler, feature_order = _load()
    if model is None or scaler is None:
        return _stub_score(features)
    if not feature_order or not all(f in features for f in feature_order):
        return _stub_score(features)
    row = np.array([[features[f] for f in feature_order]])
    scaled = scaler.transform(row)
    return round(float(model.predict_proba(scaled)[0][1]), 4)
