# SentinelTwin AI — Backend

FastAPI backend implementing the Digital Twin, Threat Prediction, Attack
Simulation, Defense Recommendation, Explainable Assistant, and Experience
Engine modules described in the project artifact.

## Setup

```bash
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Seed data

The digital twin auto-seeds from `app/data/sample_flows.csv`, a small
synthetic dataset with an embedded attack chain (external -> host -> host
-> app server -> db -> domain controller) so every endpoint returns
meaningful data immediately, without needing the full IDS datasets.

## Training on real data

Download CICIDS2017 / CSE-CIC-IDS2018 / UNSW-NB15 locally, then:

```bash
python -m app.ml.train --csv path/to/dataset.csv --out model.joblib
export MODEL_PATH=model.joblib
```

`app/routers/threats.py` and the twin ingestion pipeline can then be
pointed at `app.ml.predict.predict_anomaly_score` for real anomaly scores
instead of the synthetic ones in the sample CSV.

## Key endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/auth/register`, `/login` | JWT auth |
| `GET /api/graph` | Full digital twin graph (nodes + edges + risk scores) |
| `GET /api/graph/node/{id}` | Node detail drawer data |
| `GET /api/threats` | Ranked predicted threats |
| `POST /api/simulate` | Run an attack simulation, get step-by-step log |
| `POST /api/assistant` | Ask the explainable assistant a question |
| `GET /api/reports/executive-summary` | Executive report data |
| `GET/PUT /api/settings/preferences` | User settings |
| `POST /api/upload` | Admin backfill from CSV |
