import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("st_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("st_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export interface NodeOut {
  id: string;
  type: string;
  label: string;
  trust_score: number;
  risk_score: number;
  attributes: Record<string, unknown>;
}
export interface EdgeOut {
  source: string;
  target: string;
  type: string;
  weight: number;
}
export interface GraphOut {
  nodes: NodeOut[];
  edges: EdgeOut[];
}
export interface ThreatOut {
  id: string;
  title: string;
  probability: number;
  risk_score: number;
  path: string[];
  affected_assets: string[];
  evidence: string[];
}
export interface SimulationStep {
  step_index: number;
  node: string;
  action: string;
  risk_delta: number;
  description: string;
  tactic: string;
  technique_id: string;
  technique_name: string;
}
export interface SimulationResult {
  run_id: number;
  scenario_name: string;
  status: string;
  steps: SimulationStep[];
  peak_risk: number;
}
export interface AssistantAnswer {
  answer: string;
  confidence: number;
  sources: string[];
}
export interface RecommendationOut {
  action: string;
  score: number;
  risk_reduction: number;
  operational_cost: number;
  historical_success: number;
  rationale: string;
  is_adaptive: boolean;
  exploration_bonus: number;
}
export interface FeatureContribution {
  feature: string;
  value: number;
  shap_value: number;
}
export interface ShapExplanation {
  anomaly_score: number;
  base_value: number;
  contributions: FeatureContribution[];
  model_loaded: boolean;
}
export interface ManualPredictResult {
  anomaly_score: number;
  risk_band: string;
  model_loaded: boolean;
}

export const fetchGraph = () => api.get<GraphOut>("/graph").then((r) => r.data);
export const fetchThreats = () => api.get<ThreatOut[]>("/threats").then((r) => r.data);
export const runSimulation = (scenario_name: string, entry_node?: string) =>
  api.post<SimulationResult>("/simulate", { scenario_name, entry_node }).then((r) => r.data);
export const askAssistant = (question: string) =>
  api.post<AssistantAnswer>("/assistant", { question }).then((r) => r.data);
export const fetchExecutiveSummary = () => api.get("/reports/executive-summary").then((r) => r.data);
export const fetchRecommendations = (nodeId: string) =>
  api.get<RecommendationOut[]>(`/recommendations/${encodeURIComponent(nodeId)}`).then((r) => r.data);
export const applyRecommendation = (node_id: string, action: string, outcome: string, risk_reduced: number) =>
  api.post("/recommendations/apply", { node_id, action, outcome, risk_reduced }).then((r) => r.data);

export const login = (username: string, password: string) => {
  const form = new URLSearchParams();
  form.set("username", username);
  form.set("password", password);
  return api.post<{ access_token: string }>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  }).then((r) => r.data);
};
export const register = (username: string, password: string) =>
  api.post<{ access_token: string }>("/auth/register", { username, password }).then((r) => r.data);

export const manualPredict = (features: Record<string, number>) =>
  api.post<ManualPredictResult>("/ml/predict", { features }).then((r) => r.data);
export const manualExplain = (features: Record<string, number>) =>
  api.post<ShapExplanation>("/ml/explain", { features }).then((r) => r.data);

export interface BenchmarkResult {
  methods: Record<string, Record<string, number>>;
  correlations: Record<string, { spearman_rho: number; p_value: number }>;
  top_disagreements: { node: string; composite_score: number; naive_average: number; gap: number; composite_rank: number }[];
}
export interface CalibrationResult {
  status: string;
  labeled_node_count: number;
  minimum_required?: number;
  kendalls_tau?: number;
  p_value?: number;
  per_node?: { node: string; formula_score: number; human_consensus: number }[];
}
export interface EfficiencyResult {
  budget: number;
  candidate_count: number;
  ranked_curve: { node: string; action: string; cumulative_cost: number; cumulative_risk_reduction: number }[];
  naive_curve: { node: string; action: string; cumulative_cost: number; cumulative_risk_reduction: number }[];
  ranked_total_reduction: number;
  naive_total_reduction: number;
  ranked_advantage: number;
}

export const fetchBenchmark = () => api.get<BenchmarkResult>("/benchmark/scoring-methods").then((r) => r.data);
export const fetchCalibration = () => api.get<CalibrationResult>("/calibration/results").then((r) => r.data);
export const submitCalibrationLabel = (node_id: string, labeler: string, risk_rating: number) =>
  api.post("/calibration/label", { node_id, labeler, risk_rating }).then((r) => r.data);
export const fetchEfficiencyCurve = (budget: number) =>
  api.get<EfficiencyResult>(`/efficiency/mitigation-curve?budget=${budget}`).then((r) => r.data);