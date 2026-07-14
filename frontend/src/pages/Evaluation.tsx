import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";
import {
  fetchBenchmark, fetchCalibration, fetchEfficiencyCurve, submitCalibrationLabel,
  BenchmarkResult, CalibrationResult, EfficiencyResult,
} from "../api/client";

export default function Evaluation() {
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [calibration, setCalibration] = useState<CalibrationResult | null>(null);
  const [efficiency, setEfficiency] = useState<EfficiencyResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [labelNode, setLabelNode] = useState("");
  const [labelRating, setLabelRating] = useState(3);
  const [labelStatus, setLabelStatus] = useState<string | null>(null);

  const loadAll = () => {
    fetchBenchmark().then(setBenchmark).catch(() => setError("Benchmark failed to load."));
    fetchCalibration().then(setCalibration).catch(() => setError("Calibration failed to load."));
    fetchEfficiencyCurve(0.5).then(setEfficiency).catch(() => setError("Efficiency curve failed to load."));
  };

  useEffect(loadAll, []);

  const submitLabel = async () => {
    if (!labelNode.trim()) return;
    try {
      await submitCalibrationLabel(labelNode.trim(), "team-member", labelRating);
      setLabelStatus(`Logged blind rating ${labelRating} for ${labelNode}.`);
      setLabelNode("");
      fetchCalibration().then(setCalibration);
    } catch {
      setLabelStatus("Could not submit label — check the node id exists in the twin.");
    }
    setTimeout(() => setLabelStatus(null), 3000);
  };

  const efficiencyChartData = efficiency
    ? Array.from(
        { length: Math.max(efficiency.ranked_curve.length, efficiency.naive_curve.length) },
        (_, i) => ({
          step: i + 1,
          ranked: efficiency.ranked_curve[i]?.cumulative_risk_reduction ?? efficiency.ranked_curve.at(-1)?.cumulative_risk_reduction ?? 0,
          naive: efficiency.naive_curve[i]?.cumulative_risk_reduction ?? efficiency.naive_curve.at(-1)?.cumulative_risk_reduction ?? 0,
        })
      )
    : [];

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Evaluation</h1>
        <p className="text-sm text-muted mt-1">
          Methodology validation: does the risk formula beat naive baselines, does it match human judgment,
          and does cost-aware mitigation ranking actually outperform naive prioritization?
        </p>
      </header>

      {error && <div className="card p-4 border-warning/40 text-warning text-sm mb-6">{error}</div>}

      {/* Scoring Method Benchmark */}
      <div className="card p-5 mb-6">
        <h2 className="text-sm font-semibold mb-3">Scoring Method Benchmark</h2>
        {!benchmark && <p className="text-sm text-muted">Loading...</p>}
        {benchmark && (
          <>
            <p className="text-xs text-muted mb-3">
              Spearman rank correlation between the composite risk formula and each naive single-signal baseline.
            </p>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(benchmark.correlations).map(([method, stats]) => (
                <div key={method} className="p-3 rounded-md bg-raised border border-border">
                  <p className="text-xs text-muted font-mono">{method}</p>
                  <p className="font-mono text-lg mt-1">ρ = {stats.spearman_rho.toFixed(3)}</p>
                  <p className="text-xs text-muted mt-0.5">p = {stats.p_value.toFixed(4)}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted uppercase tracking-wide mt-4 mb-2">
              Nodes where composite differs most from naive baselines
            </p>
            <div className="space-y-1">
              {benchmark.top_disagreements.map((d) => (
                <div key={d.node} className="flex items-center justify-between text-xs font-mono">
                  <span>{d.node}</span>
                  <span className="text-muted">composite {d.composite_score} vs naive avg {d.naive_average} (gap {d.gap})</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Analyst Consensus Calibration */}
      <div className="card p-5 mb-6">
        <h2 className="text-sm font-semibold mb-3">Analyst Consensus Calibration</h2>
        <p className="text-xs text-muted mb-3">
          Submit a blind 1-5 risk rating for a node (don't check its formula score first) to validate the formula against human judgment.
        </p>
        <div className="flex gap-2 items-end mb-4">
          <div className="flex-1">
            <label className="text-xs text-muted">Node ID</label>
            <input
              value={labelNode}
              onChange={(e) => setLabelNode(e.target.value)}
              placeholder="e.g. srv-dc01"
              className="w-full mt-1 bg-raised border border-border rounded-md px-2 py-1.5 text-sm font-mono"
            />
          </div>
          <div>
            <label className="text-xs text-muted">Risk (1-5)</label>
            <input
              type="number" min={1} max={5} value={labelRating}
              onChange={(e) => setLabelRating(parseInt(e.target.value) || 1)}
              className="w-20 mt-1 bg-raised border border-border rounded-md px-2 py-1.5 text-sm font-mono"
            />
          </div>
          <button className="btn-primary" onClick={submitLabel}>Submit Label</button>
        </div>
        {labelStatus && <p className="text-xs text-accent mb-3">{labelStatus}</p>}

        {calibration?.status === "insufficient_data" && (
          <p className="text-sm text-muted">
            {calibration.labeled_node_count} of {calibration.minimum_required} minimum labels collected so far.
          </p>
        )}
        {calibration?.status === "computed" && (
          <div>
            <p className="font-mono text-lg">Kendall's τ = {calibration.kendalls_tau?.toFixed(3)}</p>
            <p className="text-xs text-muted mb-3">based on {calibration.labeled_node_count} labeled nodes, p = {calibration.p_value?.toFixed(4)}</p>
            <div className="space-y-1">
              {calibration.per_node?.map((n) => (
                <div key={n.node} className="flex justify-between text-xs font-mono">
                  <span>{n.node}</span>
                  <span className="text-muted">formula {n.formula_score} vs human {n.human_consensus}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Mitigation Efficiency Curve */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold mb-3">Mitigation Efficiency Curve</h2>
        {!efficiency && <p className="text-sm text-muted">Loading...</p>}
        {efficiency && (
          <>
            <p className="text-xs text-muted mb-3">
              Cumulative risk reduction achieved under a fixed effort budget ({efficiency.budget}), comparing
              adaptive cost-aware ranking against naive risk-only prioritization.
            </p>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={efficiencyChartData}>
                <CartesianGrid stroke="#1E2A44" vertical={false} />
                <XAxis dataKey="step" tick={{ fill: "#8A96AC", fontSize: 11 }} label={{ value: "Actions applied", position: "insideBottom", offset: -2, fill: "#8A96AC", fontSize: 11 }} />
                <YAxis tick={{ fill: "#8A96AC", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#172136", border: "1px solid #1E2A44", borderRadius: 8, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="ranked" name="Adaptive (cost-aware)" stroke="#2DD4BF" strokeWidth={2} />
                <Line type="monotone" dataKey="naive" name="Naive (risk-only)" stroke="#F59E0B" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
              <div>
                <p className="text-xs text-muted uppercase">Adaptive Total</p>
                <p className="font-mono text-lg mt-1 text-[#2DD4BF]">{efficiency.ranked_total_reduction.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted uppercase">Naive Total</p>
                <p className="font-mono text-lg mt-1 text-warning">{efficiency.naive_total_reduction.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted uppercase">Advantage</p>
                <p className={`font-mono text-lg mt-1 ${efficiency.ranked_advantage >= 0 ? "text-success" : "text-critical"}`}>
                  {efficiency.ranked_advantage >= 0 ? "+" : ""}{efficiency.ranked_advantage.toFixed(2)}
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}