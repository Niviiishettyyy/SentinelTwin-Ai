"""
Preprocessing for IDS datasets (CICIDS2017 / CSE-CIC-IDS2018 / UNSW-NB15).

Run locally against the full downloaded CSVs (this scaffold's sandbox has
no internet access to fetch multi-GB datasets). Produces a cleaned
feature matrix + label vector ready for app.ml.train.
"""
import pandas as pd

NUMERIC_FEATURE_HINTS = [
    "duration", "flow_duration", "tot_fwd_pkts", "tot_bwd_pkts",
    "flow_byts_s", "flow_pkts_s", "fwd_pkt_len_mean", "bwd_pkt_len_mean",
]


def load_and_clean(csv_path: str, label_col: str = "label") -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.replace([float("inf"), float("-inf")], pd.NA).dropna()

    if label_col not in df.columns and "Label".lower() in df.columns:
        label_col = "label"

    return df


def select_features(df: pd.DataFrame, label_col: str = "label"):
    feature_cols = [c for c in df.columns if c != label_col and df[c].dtype != object]
    X = df[feature_cols]
    y = (df[label_col].astype(str).str.lower() != "benign").astype(int)
    return X, y, feature_cols
