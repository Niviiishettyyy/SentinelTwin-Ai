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
