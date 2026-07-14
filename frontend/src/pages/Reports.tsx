import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { fetchExecutiveSummary } from "../api/client";
import jsPDF from "jspdf";

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
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchExecutiveSummary()
      .then((d) => setSummary(d as Summary))
      .catch(() => setError("Could not load report data. Is the backend running and are you logged in?"));
  }, []);

  const chartData = summary?.top_risk_nodes.map(([node, score]) => ({ node, risk: score })) ?? [];

  const exportPdf = () => {
    if (!summary) return;
    setExporting(true);
    try {
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const marginX = 48;
      let y = 56;

      doc.setFontSize(18);
      doc.setFont("helvetica", "bold");
      doc.text("SentinelTwin AI — Incident Report", marginX, y);
      y += 20;

      doc.setFontSize(9);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(120);
      doc.text(`Generated ${new Date().toLocaleString()}`, marginX, y);
      doc.setTextColor(0);
      y += 28;

      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("Summary", marginX, y);
      y += 18;
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.text(`Assets monitored: ${summary.device_count}`, marginX, y); y += 16;
      doc.text(`Flagged flows: ${summary.flagged_flows}`, marginX, y); y += 16;
      doc.text(`Average risk: ${summary.average_risk.toFixed(2)}`, marginX, y); y += 16;
      doc.text(`Disruption level: ${summary.business_impact.disruption_level}`, marginX, y); y += 16;
      doc.text(`Estimated recovery time: ${summary.business_impact.estimated_recovery_hours} hrs`, marginX, y); y += 28;

      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("Top Risk Assets", marginX, y);
      y += 18;
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      summary.top_risk_nodes.forEach(([node, score]) => {
        doc.text(`${node}  —  risk ${score.toFixed(2)}`, marginX, y);
        y += 15;
      });
      y += 14;

      if (summary.business_impact.critical_assets_at_risk.length > 0) {
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("Critical Assets at Risk", marginX, y);
        y += 18;
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        summary.business_impact.critical_assets_at_risk.forEach((asset) => {
          doc.text(`- ${asset}`, marginX, y);
          y += 15;
        });
        y += 14;
      }

      if (summary.recent_simulations.length > 0) {
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("Recent Simulations", marginX, y);
        y += 18;
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        summary.recent_simulations.forEach((s) => {
          doc.text(`${s.scenario} — peak risk ${s.peak_risk.toFixed(2)} (${s.status})`, marginX, y);
          y += 15;
        });
      }

      doc.save(`sentineltwin-report-${new Date().toISOString().slice(0, 10)}.pdf`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div>
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Reports</h1>
          <p className="text-sm text-muted mt-1">Executive-level summary of risk, trends, and recent activity.</p>
        </div>
        <button
          onClick={exportPdf}
          disabled={!summary || exporting}
          className="btn-primary"
        >
          {exporting ? "Exporting..." : "Export PDF"}
        </button>
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