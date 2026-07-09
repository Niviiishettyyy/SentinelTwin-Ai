import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SummaryCard from "../components/SummaryCard";
import { fetchExecutiveSummary } from "../api/client";

interface Summary {
  device_count: number;
  flagged_flows: number;
  average_risk: number;
  top_risk_nodes: [string, number][];
  recent_simulations: { id: number; scenario: string; peak_risk: number; status: string }[];
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchExecutiveSummary()
      .then((d) => setSummary(d as Summary))
      .catch(() => setError("Could not load dashboard data. Is the backend running and are you logged in?"));
  }, []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="text-sm text-muted mt-1">Current state of the organization's digital twin.</p>
      </header>

      {error && (
        <div className="card p-4 border-warning/40 text-warning text-sm mb-6">{error}</div>
      )}

      {!summary && !error && (
        <div className="text-muted text-sm">Loading twin state...</div>
      )}

      {summary && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard
              label="Monitored Assets"
              value={summary.device_count}
              sub="devices, servers & apps in the twin"
              onClick={() => navigate("/twin")}
            />
            <SummaryCard
              label="Flagged Flows"
              value={summary.flagged_flows}
              tone={summary.flagged_flows > 0 ? "critical" : "success"}
              sub="anomalous connections detected"
              onClick={() => navigate("/threats")}
            />
            <SummaryCard
              label="Average Risk"
              value={summary.average_risk.toFixed(2)}
              tone={summary.average_risk > 0.5 ? "warning" : "success"}
              sub="mean node risk score (0-1)"
              onClick={() => navigate("/twin")}
            />
            <SummaryCard
              label="Simulations Run"
              value={summary.recent_simulations.length}
              sub="recent attack simulations"
              onClick={() => navigate("/simulation")}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
            <div className="card p-5">
              <h2 className="text-sm font-semibold mb-3">Top Risk Nodes</h2>
              <ul className="space-y-2">
                {summary.top_risk_nodes.map(([node, score]) => (
                  <li key={node} className="flex items-center justify-between text-sm">
                    <span className="font-mono text-muted">{node}</span>
                    <span className={`pill ${score > 0.6 ? "pill-critical" : score > 0.35 ? "pill-warning" : "pill-success"}`}>
                      {score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card p-5">
              <h2 className="text-sm font-semibold mb-3">Recent Simulations</h2>
              {summary.recent_simulations.length === 0 ? (
                <p className="text-sm text-muted">No simulations run yet. Head to Simulation Center to start one.</p>
              ) : (
                <ul className="space-y-2">
                  {summary.recent_simulations.map((s) => (
                    <li key={s.id} className="flex items-center justify-between text-sm">
                      <span>{s.scenario}</span>
                      <span className="pill pill-muted">peak {s.peak_risk.toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
