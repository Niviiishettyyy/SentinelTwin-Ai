from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str


class NodeOut(BaseModel):
    id: str
    type: str
    label: str
    trust_score: float
    risk_score: float
    attributes: Dict[str, Any] = {}


class EdgeOut(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 1.0


class GraphOut(BaseModel):
    nodes: List[NodeOut]
    edges: List[EdgeOut]


class ThreatOut(BaseModel):
    id: str
    title: str
    probability: float
    risk_score: float
    path: List[str]
    affected_assets: List[str]
    evidence: List[str]


class SimulationRequest(BaseModel):
    scenario_name: str
    entry_node: Optional[str] = None


class SimulationStep(BaseModel):
    step_index: int
    node: str
    action: str
    risk_delta: float
    description: str
    # --- MITRE ATT&CK mapping (new) ---
    tactic: str = "Unknown"
    technique_id: str = "N/A"
    technique_name: str = "N/A"


class SimulationResult(BaseModel):
    run_id: int
    scenario_name: str
    status: str
    steps: List[SimulationStep]
    peak_risk: float


class RecommendationOut(BaseModel):
    action: str
    score: float
    risk_reduction: float
    operational_cost: float
    historical_success: float
    rationale: str
    # --- Adaptive/bandit engine fields (new) ---
    is_adaptive: bool = False
    exploration_bonus: float = 0.0


class AssistantQuery(BaseModel):
    question: str


class AssistantAnswer(BaseModel):
    answer: str
    confidence: float
    sources: List[str]


# --- SHAP explainability (new) ---
class FeatureContribution(BaseModel):
    feature: str
    value: float
    shap_value: float


class ShapExplanation(BaseModel):
    anomaly_score: float
    base_value: float
    contributions: List[FeatureContribution]
    model_loaded: bool