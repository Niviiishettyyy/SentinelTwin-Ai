from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, graph, threats, simulate, assistant, reports, settings, upload, recommendations, ml, benchmark, calibration, efficiency, sweep

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelTwin AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(graph.router)
app.include_router(threats.router)
app.include_router(simulate.router)
app.include_router(assistant.router)
app.include_router(reports.router)
app.include_router(settings.router)
app.include_router(upload.router)
app.include_router(recommendations.router)
app.include_router(ml.router)
app.include_router(benchmark.router)
app.include_router(calibration.router)
app.include_router(efficiency.router)
app.include_router(sweep.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SentinelTwin AI"}
