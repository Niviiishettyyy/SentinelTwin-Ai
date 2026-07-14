import { useState } from "react";
import { manualPredict, manualExplain, ManualPredictResult, ShapExplanation } from "../api/client";

const DEFAULT_FEATURES: Record<string, number> = {
  bytes_per_packet: 100, dbytes: 2000, dmean: 300, dpkts: 5, dur: 1.2,
  fwd_bwd_byte_ratio: 0.3, fwd_bwd_packet_ratio: 0.5, rate: 5000,
  sbytes: 400, sinpkt: 900000, sload: 1000000, smean: 350, spkts: 10,
};

export default function ModelPlayground() {
  const [features, setFeatures] = useState(DEFAULT_FEATURES);
  const [result, setResult] = useState<ManualPredictResult | null>(null);
  const [explanation, setExplanation] = useState<ShapExplanation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [explaining, setExplaining] = useState(false);

  const run = async () => {
    setLoading(true);
    setError(null);
    setExplanation(null);
    try {
      const r = await manualPredict(features);
      setResult(r);
    } catch {
      setError("Prediction failed. Is the backend running and are you logged in?");
    } finally {
      setLoading(false);
    }
  };

  const explain = async () => {
    setExplaining(true);
    setError(null);
    try {
      const r = await manualExplain(features);
      setExplanation(r);
    } catch {
      setError("Explanation failed — make sure `shap` is installed on the backend (pip install shap).");
    } finally {
      setExplaining(false);
    }
  };

  const maxAbsShap = explanation
    ? Math.max(...explanation.contributions.map((c) => Math.abs(c.shap_value)), 0.0001)
    : 1;

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Model Playground</h1>
        <p className="text-sm text-muted mt-1">
          Manually enter flow features, run them through the trained RandomForest classifier directly, and see
          real per-feature SHAP contributions — independent of any twin node.
        </p>
      </header>

      <div className="card p-5">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(features).map(([key, val]) => (
            <div key={key}>
              <label className="text-xs text-muted font-mono">{key}</label>
              <input
                type="number"
                value={val}
                onChange={(e) => setFeatures((f) => ({ ...f, [key]: parseFloat(e.target.value) || 0 }))}
                className="w-full mt-1 bg-raised border border-border rounded-md px-2 py-1.5 text-sm font-mono outline-none focus:border-[#2DD4BF]/50"
              />
            </div>
          ))}
        </div>

        <div className="flex gap-3 mt-5">
          <button className="btn-primary" onClick={run} disabled={loading}>
            {loading ? "Running..." : "Run Prediction"}
          </button>
          <button
            className="px-4 py-2 rounded-md border border-[#2DD4BF]/40 text-[#2DD4BF] text-sm hover:bg-[#2DD4BF]/10 transition"
            onClick={explain}
            disabled={explaining}
          >
            {explaining ? "Explaining..." : "Explain with SHAP"}
          </button>
        </div>

        {error && <p className="text-[#F43F5E] text-sm mt-3">{error}</p>}

        {result && (
          <div className="mt-5 p-4 rounded-md bg-raised border border-border">
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted uppercase">Anomaly Score</span>
              <span className="font-mono text-lg">{result.anomaly_score.toFixed(4)}</span>
              <span className={`pill ${
                result.risk_band === "critical" ? "pill-critical" : result.risk_band === "elevated" ? "pill-warning" : "pill-success"
              }`}>
                {result.risk_band}
              </span>
            </div>
            <p className="text-xs text-muted mt-2">
              {result.model_loaded
                ? "Computed by the real trained model."
                : "Model files not found on the server — this is the deterministic fallback score, not the trained model."}
            </p>
          </div>
        )}

        {explanation && explanation.contributions.length > 0 && (
          <div className="mt-4 p-4 rounded-md bg-raised border border-border">
            <p className="text-xs text-muted uppercase tracking-wide mb-1">
              SHAP Feature Contributions (base value {explanation.base_value.toFixed(4)})
            </p>
            <p className="text-xs text-muted mb-3">
              Bars show how much each feature pushed the prediction up (red) or down (green) from the base value.
            </p>
            <div className="space-y-1.5">
              {explanation.contributions.map((c) => {
                const widthPct = (Math.abs(c.shap_value) / maxAbsShap) * 100;
                const positive = c.shap_value >= 0;
                return (
                  <div key={c.feature} className="flex items-center gap-2 text-xs">
                    <span className="w-40 font-mono text-muted truncate">{c.feature}</span>
                    <div className="flex-1 h-4 bg-[#0B0F14] rounded relative overflow-hidden">
                      <div
                        className={`h-full ${positive ? "bg-[#F43F5E]" : "bg-[#34D399]"}`}
                        style={{ width: `${widthPct}%`, marginLeft: positive ? "50%" : `${50 - widthPct}%` }}
                      />
                      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-border" />
                    </div>
                    <span className="w-16 font-mono text-right">{c.shap_value.toFixed(4)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {explanation && explanation.contributions.length === 0 && (
          <p className="text-xs text-muted mt-4">
            No SHAP contributions returned — either `shap` isn't installed on the backend, or the model/scaler
            aren't loaded. The anomaly score above still reflects the real model if `model_loaded` is true.
          </p>
        )}
      </div>
    </div>
  );
}