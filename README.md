# SentinelTwin AI

Predict. Simulate. Learn. Protect.

Full-stack scaffold implementing the SentinelTwin AI project artifact:
a cognitive cyber defense platform with a live digital twin, threat
prediction, safe attack simulation, defense recommendation, an
explainable assistant, and an experience engine that learns from past
incidents.

## Structure

```
sentineltwin/
  backend/     FastAPI + SQLAlchemy + NetworkX + scikit-learn
  frontend/    React + TypeScript + Tailwind + React Flow + Recharts
```

## Quick start

**Terminal 1 — backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. Register a user via `POST
http://localhost:8000/api/auth/register` (or the `/docs` Swagger UI),
store the returned token in `localStorage.st_token`, and the app is
fully live against the seeded synthetic attack-chain data.

## What's real vs. stubbed in this scaffold

| Module | Status |
|---|---|
| Digital Twin graph (NetworkX) | Real — builds from `sample_flows.csv`, swap in real dataset replay |
| Risk scoring formula (Section 9b) | Real — implemented in `app/graph/scoring.py` |
| Attack simulation engine | Real — weighted graph traversal in `app/graph/simulate_engine.py` |
| Threat prediction | Real — derived from flagged edges + risk scores |
| Explainable Assistant | Stubbed — keyword/graph-matching, not yet a real LLM+RAG pipeline |
| ML anomaly classifier | Scaffolded — `app/ml/train.py` ready to run against real IDS datasets locally; falls back to a deterministic stub until a model is trained |
| Experience Engine ledger | Real — SQLite-backed incident log with historical success lookup |
| Auth | Real — JWT via FastAPI |

See `backend/README.md` and `frontend/README.md` for module-specific
detail, and the project artifact doc (Section 19) for the phased build
roadmap this scaffold maps onto.
