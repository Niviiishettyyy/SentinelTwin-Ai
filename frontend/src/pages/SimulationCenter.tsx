import { useState } from "react";
import { runSimulation, SimulationResult } from "../api/client";

const SCENARIOS = [
  "External Foothold -> Lateral Movement -> Domain Compromise",
  "Insider Credential Misuse",
  "Ransomware Propagation",
];

export default function SimulationCenter() {
  const [scenario, setScenario] = useState(SCENARIOS[0]);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await runSimulation(scenario);
      setResult(r);
      setActiveStep(0);
    } catch {
      setError("Simulation failed to start. Is the backend running and are you logged in?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Simulation Center</h1>
        <p className="text-sm text-muted mt-1">Choose a scenario, run it safely inside the twin, and step through the timeline.</p>
      </header>

      <div className="card p-5 mb-6">
        <label className="text-xs text-muted uppercase tracking-wide">Scenario</label>
        <div className="flex gap-3 mt-2">
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            className="flex-1 bg-raised border border-border rounded-md px-3 py-2 text-sm"
          >
            {SCENARIOS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button className="btn-primary" onClick={start} disabled={loading}>
            {loading ? "Running..." : "Run Simulation"}
          </button>
        </div>
        {error && <p className="text-warning text-sm mt-3">{error}</p>}
      </div>

      {result && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold">Attack Timeline</h2>
            <span className="pill pill-critical">peak risk {result.peak_risk.toFixed(2)}</span>
          </div>

          {result.steps.length === 0 ? (
            <p className="text-sm text-muted">No traversable path found from the chosen entry point.</p>
          ) : (
            <>
              <div className="flex items-center gap-1 mb-6">
                {result.steps.map((s, i) => (
                  <button
                    key={s.step_index}
                    onClick={() => setActiveStep(i)}
                    className={`h-2 flex-1 rounded-full transition ${i <= activeStep ? "bg-accent" : "bg-border"}`}
                    title={s.node}
                  />
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2 space-y-2">
                  {result.steps.map((s, i) => (
                    <button
                      key={s.step_index}
                      onClick={() => setActiveStep(i)}
                      className={`w-full text-left px-3 py-2 rounded-md border text-sm transition ${
                        i === activeStep
                          ? "border-accent/50 bg-accent/10"
                          : "border-border hover:border-accent/30"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono">{s.node}</span>
                        <span className="pill pill-warning">risk {s.risk_delta.toFixed(2)}</span>
                      </div>
                      <p className="text-xs text-muted mt-1">{s.description}</p>
                    </button>
                  ))}
                </div>

                <div className="card p-4 bg-raised">
                  <p className="text-xs text-muted uppercase tracking-wide mb-2">Step {activeStep + 1} of {result.steps.length}</p>
                  <p className="font-mono text-sm">{result.steps[activeStep].node}</p>
                  <p className="text-sm text-muted mt-2">{result.steps[activeStep].description}</p>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
