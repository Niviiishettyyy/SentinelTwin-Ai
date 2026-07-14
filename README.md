# SentinelTwin AI

SentinelTwin AI is a full-stack cyber defense platform that combines a live digital twin, threat prediction, attack simulation, adaptive recommendations, explainable ML, and reporting into a single research-ready application.

The project is designed to help security teams reason about attack paths, score risk, simulate adversary movement, and prioritize mitigations using data-driven signals rather than static rule sets.

![System architecture placeholder](docs/architecture.png)

## Project Overview

SentinelTwin AI transforms network telemetry and simulated attack-chain data into a continuously updated digital twin of an environment. The system ingests graph-based flow information, assigns risk to nodes and edges, simulates probable attack paths, and exposes an explainable recommendation layer for defenders.

## Problem Statement

Modern security operations teams need to answer three questions quickly:

- Where is the most critical risk in the environment?
- What is the most likely next attack path?
- Which mitigation should be prioritized first?

Traditional dashboards often provide static alerts without actionable context. SentinelTwin AI aims to close that gap by combining graph-based reasoning with ML-driven scoring and explainability.

## Motivation

This project was built to demonstrate a practical, end-to-end approach to cyber defense decision support using:

- graph analytics for network structure and attack propagation,
- anomaly scoring for suspicious behavior,
- adaptive defense recommendations,
- explainable AI for analyst trust,
- and a reusable API/frontend foundation for experimentation.

## Key Contributions

- A live digital twin of a network represented as a directed graph.
- A risk-scoring framework for nodes and edges.
- An attack simulation engine that proposes likely action sequences.
- A recommendation engine that balances risk reduction, cost, and historical outcomes.
- An explainable ML and SHAP-based playground for anomaly interpretation.
- A reporting and evaluation layer for benchmark, calibration, and efficiency analysis.

## Features

- Digital Twin visualization and node/edge inspection
- Threat ranking based on graph risk and anomaly signals
- Attack simulation with MITRE ATT&CK-style mapping
- Continuous attack sweep across multiple entry points
- Adaptive recommendation scoring
- SHAP-based explainability for ML predictions
- AI assistant with explainable, rule-based responses
- Executive reporting and evaluation metrics

## Technology Stack

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- NetworkX
- scikit-learn
- pandas
- numpy
- joblib
- SHAP
- SQLite

### Frontend
- React
- TypeScript
- Vite
- React Router
- React Flow
- Recharts
- Tailwind CSS
- jsPDF
- Lucide icons

## Complete System Architecture

The system is organized into four major layers:

1. Data Layer
   - Seed data is loaded from the synthetic sample flow dataset.
   - The backend builds the digital twin graph from this data.

2. Intelligence Layer
   - Risk scoring is computed for graph nodes and edges.
   - ML workflows provide anomaly scores and explainability.
   - Recommendation logic combines graph risk with historical performance.

3. Simulation and Decision Layer
   - Attack paths are simulated using graph traversal.
   - Continuous sweep explores multiple entry points.
   - Benchmarking, calibration, and efficiency analyses support understanding of the recommendation strategy.

4. Experience and Presentation Layer
   - The FastAPI backend exposes REST endpoints.
   - The React frontend provides dashboards, twin views, simulation controls, reports, and evaluation tools.

### Architecture placeholders

- [System architecture](docs/architecture.png)
- [Workflow diagram](docs/workflow.png)
- [Dashboard view](docs/dashboard.png)
- [Digital twin view](docs/digital_twin.png)
- [Simulation view](docs/simulation.png)
- [Reports view](docs/reports.png)
- [Evaluation view](docs/evaluation.png)

## Dataset

The project currently uses a combination of seeded and supported datasets.

### UNSW-NB15
- A widely used intrusion detection benchmark dataset.
- Supported as a future-ready target for model retraining.

### CICIDS2017
- A benchmark network intrusion dataset.
- Intended for use in replacing the synthetic baseline with real-world training data.

### CSE-CIC-IDS2018
- A larger-scale intrusion dataset for more comprehensive experimentation.
- Suitable for extending model coverage and robustness.

### sample_flows.csv
- The repository includes a synthetic flow dataset in the backend data directory.
- This dataset is used to seed the digital twin and provide immediate, meaningful outputs without requiring external datasets.

## Machine Learning Model

The backend includes a machine-learning pipeline for anomaly scoring and explainability.

- Training logic is implemented in the backend ML module.
- The model is intended to be trained on datasets such as UNSW-NB15, CICIDS2017, or CSE-CIC-IDS2018.
- If a trained model is not available, the application falls back to a deterministic scoring heuristic.

## Risk Scoring

The scoring module computes risk for nodes and edges based on graph structure, propagation potential, and anomaly indicators. This output is used by the threat ranking, simulation engine, and recommendation layer.

## Digital Twin

The digital twin is implemented as a directed graph representation of the environment. It captures connectivity, critical assets, and likely attack movement through the network. The twin is used by the simulation, recommendations, reports, and threat analysis components.

## Attack Simulation

The attack simulation engine explores likely attack progression from a chosen entry point through the graph. Each simulated step is logged with context and risk progression.

## Continuous Sweep

The continuous sweep feature explores multiple entry points and evaluates how an attack might propagate across the network. This allows defenders to examine the broader attack surface rather than a single path.

## MITRE ATT&CK Mapping

Simulation steps are heuristically mapped to MITRE ATT&CK tactics and techniques to provide contextual labels for the attack narrative.

## Adaptive Recommendation Engine

The recommendation engine ranks mitigations based on a balance of:

- risk reduction potential,
- operational cost,
- historical success,
- and the current graph context.

## SHAP Explainability

The backend ML module supports SHAP-based explanations when a compatible trained model is available. These explanations help analysts understand which features contribute most to an anomaly score.

## AI Assistant

The assistant is currently a rule-based, explainable component that responds using graph and scoring context. A future LLM/RAG-based assistant is planned as a next-stage enhancement.

## Reports

The reporting layer aggregates system state and simulation outcomes into executive-friendly summaries. The frontend includes report views and export-oriented workflows.

## Evaluation Module

The project includes evaluation-focused modules for:

- scoring method benchmarking,
- calibration analysis,
- efficiency curves,
- and recommendation quality assessment.

## API Endpoints

The backend exposes REST endpoints under the following areas:

- Authentication: `/api/auth/register`, `/api/auth/login`
- Graph: `/api/graph`, `/api/graph/node/{id}`
- Threats: `/api/threats`
- Simulation: `/api/simulate`
- Recommendations: `/api/recommendations/{node_id}`
- Assistant: `/api/assistant`
- Reports: `/api/reports/executive-summary`
- Settings: `/api/settings/preferences`
- ML Playground: `/api/ml/predict`, `/api/ml/explain`
- Evaluation endpoints: `/api/benchmark`, `/api/calibration`, `/api/efficiency`, `/api/sweep`

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Frontend
```bash
cd frontend
npm install
```

## Running the Project

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 and use the application.

## Folder Structure

```text
SentinelTwin-AI/
├── backend/
├── frontend/
├── docs/
├── README.md
├── requirements.txt
├── LICENSE
└── .env.example
```

## Future Work

Planned enhancements include:

- integration with real-world IDS datasets at scale,
- a production-grade LLM/RAG assistant,
- richer visual analytics and dashboards,
- persistence and deployment hardening,
- and expanded evaluation and benchmarking workflows.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

