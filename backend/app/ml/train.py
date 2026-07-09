"""
Trains the anomaly/attack classifier (Section 1, Phase 1 of the roadmap).

Usage (run locally, after downloading CICIDS2017 / CSE-CIC-IDS2018):
    python -m app.ml.train --csv path/to/cicids2017_sample.csv --out model.joblib
"""
import argparse
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

from app.ml.preprocess import load_and_clean, select_features


def train(csv_path: str, out_path: str, label_col: str = "label"):
    df = load_and_clean(csv_path, label_col)
    X, y, feature_cols = select_features(df, label_col)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=None, n_jobs=-1, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, preds))
    print("ROC-AUC:", roc_auc_score(y_test, probs))

    joblib.dump({"model": clf, "feature_cols": feature_cols}, out_path)
    print(f"Saved model to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default="model.joblib")
    parser.add_argument("--label-col", default="label")
    args = parser.parse_args()
    train(args.csv, args.out, args.label_col)
