import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { fetchExecutiveSummary } from "../api/client";

interface Summary {
  device_count: number;
  flagged_flows: number;
  average_risk: number;
  top_risk_nodes: [string, number][];
  business_impact: {
    disruption_level: string;
    estimated_recovery_hours: string;
    critical_assets_at_risk: string[];
  };
  recent_simulations: { id: number; scenario: string; peak_risk: number; status: string }[];
}

export default function Reports() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchExecutiveSummary()
      .then((d) => setSummary(d as Summary))
      .catch(() => setError("Could not load report data. Is the backend running and are you logged in?"));
  }, []);

  const chartData = summary?.top_risk_nodes.map(([node, score]) => ({ node, risk: score })) ?? [];

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Reports</h1>
        <p className="text-sm text-muted mt-1">Executive-level summary of risk, trends, and recent activity.</p>
      </header>

      {error && <div className="card p-4 border-warning/40 text-warning text-sm mb-6">{error}</div>}

      {summary && (
        <div className="card p-5">
          <h2 className="text-sm font-semibold mb-4">Risk by Top Asset</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid stroke="#1E2A44" vertical={false} />
              <XAxis dataKey="node" tick={{ fill: "#8A96AC", fontSize: 11 }} />
              <YAxis domain={[0, 1]} tick={{ fill: "#8A96AC", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#172136", border: "1px solid #1E2A44", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#E6EAF2" }}
              />
              <Bar dataKey="risk" fill="#38BDF8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-3 gap-4 mt-6 text-sm">
            <div>
              <p className="text-xs text-muted uppercase">Assets Monitored</p>
              <p className="font-mono text-lg mt-1">{summary.device_count}</p>
            </div>
            <div>
              <p className="text-xs text-muted uppercase">Flagged Flows</p>
              <p className="font-mono text-lg mt-1">{summary.flagged_flows}</p>
            </div>
            <div>
              <p className="text-xs text-muted uppercase">Average Risk</p>
              <p className="font-mono text-lg mt-1">{summary.average_risk.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}

      {summary && (
        <div className="card p-5 mt-6">
          <h2 className="text-sm font-semibold mb-4">Business Impact</h2>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-xs text-muted uppercase">Disruption Level</p>
              <span className={`pill mt-1 inline-block ${
                summary.business_impact.disruption_level === "High" ? "pill-critical"
                : summary.business_impact.disruption_level === "Moderate" ? "pill-warning"
                : "pill-success"
              }`}>
                {summary.business_impact.disruption_level}
              </span>
            </div>
            <div>
              <p className="text-xs text-muted uppercase">Est. Recovery Time</p>
              <p className="font-mono text-lg mt-1">{summary.business_impact.estimated_recovery_hours} hrs</p>
            </div>
            <div>
              <p className="text-xs text-muted uppercase">Critical Assets at Risk</p>
              <p className="font-mono text-sm mt-1">{summary.business_impact.critical_assets_at_risk.length || "None"}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
