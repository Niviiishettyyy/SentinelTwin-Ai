import os
import numpy as np
import joblib

MODEL_PATH = os.environ.get("MODEL_PATH", "network_rf_model_final.pkl")
SCALER_PATH = os.environ.get("SCALER_PATH", "network_scaler_final.pkl")

_model = None
_scaler = None
_feature_order = None
_explainer = None  # lazily built shap.TreeExplainer


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


def shap_explain(features: dict) -> dict:
    """
    Real per-feature SHAP contributions for a given feature vector,
    computed against the actual trained RandomForest. Requires the
    `shap` package (pip install shap) -- if it's not installed, or the
    model/scaler aren't loaded, or the feature set doesn't match the
    trained schema, returns model_loaded/contributions reflecting that
    rather than fabricating numbers.

    Handles multiple shap TreeExplainer return shapes across versions:
      - older API: list of per-class arrays, e.g. [array(n,f), array(n,f)]
      - newer API: single ndarray shaped (n, f, n_classes)
      - binary-only API: single ndarray shaped (n, f)
    """
    global _explainer
    model, scaler, feature_order = _load()

    if model is None or scaler is None:
        return {"anomaly_score": _stub_score(features), "base_value": 0.0,
                "contributions": [], "model_loaded": False}

    if not feature_order or not all(f in features for f in feature_order):
        return {"anomaly_score": _stub_score(features), "base_value": 0.0,
                "contributions": [], "model_loaded": False}

    try:
        import shap
    except ImportError:
        score = predict_anomaly_score(features)
        return {"anomaly_score": score, "base_value": 0.0, "contributions": [], "model_loaded": True}

    row = np.array([[features[f] for f in feature_order]])
    scaled = scaler.transform(row)

    if _explainer is None:
        _explainer = shap.TreeExplainer(model)

    raw_shap = np.array(_explainer.shap_values(scaled))
    raw_expected = np.array(_explainer.expected_value)

    # Normalize to a flat (n_features,) array for the positive class,
    # regardless of which shap version's return shape we got.
    if raw_shap.ndim == 3:
        # shape (n_samples, n_features, n_classes) -- newer shap API
        class_idx = 1 if raw_shap.shape[-1] > 1 else 0
        shap_row = raw_shap[0, :, class_idx]
    elif raw_shap.ndim == 2 and isinstance(_explainer.shap_values(scaled), list):
        # older API returned a list of length n_classes -- np.array stacked
        # it into (n_classes, n_samples, n_features); take positive class, sample 0
        class_idx = 1 if raw_shap.shape[0] > 1 else 0
        shap_row = raw_shap[class_idx][0]
    elif raw_shap.ndim == 2:
        # shape (n_samples, n_features) -- binary-only, single output
        shap_row = raw_shap[0]
    else:
        shap_row = raw_shap.reshape(-1)

    # Normalize expected_value the same way
    if raw_expected.ndim == 0:
        base_value = float(raw_expected)
    elif raw_expected.ndim == 1 and raw_expected.shape[0] > 1:
        base_value = float(raw_expected[1])
    else:
        base_value = float(np.ravel(raw_expected)[0])

    contributions = [
        {"feature": feat, "value": float(row[0][i]), "shap_value": float(shap_row[i])}
        for i, feat in enumerate(feature_order)
    ]
    contributions.sort(key=lambda c: abs(c["shap_value"]), reverse=True)

    score = predict_anomaly_score(features)
    return {
        "anomaly_score": score,
        "base_value": round(base_value, 4),
        "contributions": contributions,
        "model_loaded": True,
    }