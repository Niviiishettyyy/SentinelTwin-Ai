import { useEffect, useState } from "react";
import { fetchThreats, fetchRecommendations, applyRecommendation, ThreatOut, RecommendationOut } from "../api/client";

export default function Threats() {
  const [threats, setThreats] = useState<ThreatOut[] | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [recs, setRecs] = useState<Record<string, RecommendationOut[]>>({});
  const [recsLoading, setRecsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [appliedNote, setAppliedNote] = useState<string | null>(null);

  useEffect(() => {
    fetchThreats().then(setThreats).catch(() => setError("Could not load threats. Is the backend running and are you logged in?"));
  }, []);

  const toggle = async (t: ThreatOut) => {
    const isOpen = expanded === t.id;
    setExpanded(isOpen ? null : t.id);
    if (!isOpen && !recs[t.id] && t.affected_assets.length > 0) {
      setRecsLoading(true);
      try {
        const nodeId = t.affected_assets[0];
        const r = await fetchRecommendations(nodeId);
        setRecs((prev) => ({ ...prev, [t.id]: r }));
      } catch {
        // Recommendations are supplementary; fail silently and just show evidence.
      } finally {
        setRecsLoading(false);
      }
    }
  };

  const apply = async (t: ThreatOut, rec: RecommendationOut) => {
    try {
      await applyRecommendation(t.affected_assets[0], rec.action, "contained", rec.risk_reduction);
      setAppliedNote(`Logged "${rec.action}" as applied — future recommendations will factor this in.`);
      setTimeout(() => setAppliedNote(null), 3000);
    } catch {
      setAppliedNote("Could not log the action. Is the backend running?");
    }
  };

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Threats</h1>
        <p className="text-sm text-muted mt-1">Predicted threats ranked by risk. Expand a row for evidence and recommended defenses.</p>
      </header>

      {error && <div className="card p-4 border-warning/40 text-warning text-sm mb-6">{error}</div>}
      {!threats && !error && <p className="text-sm text-muted">Loading threats...</p>}
      {threats && threats.length === 0 && (
        <div className="card p-6 text-sm text-muted">No flagged threats in the current twin state.</div>
      )}
      {appliedNote && <div className="card p-3 border-accent/40 text-accent text-sm mb-4">{appliedNote}</div>}

      <div className="space-y-3">
        {threats?.map((t) => {
          const isOpen = expanded === t.id;
          const threatRecs = recs[t.id];
          return (
            <div key={t.id} className="card overflow-hidden">
              <button
                onClick={() => toggle(t)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
              >
                <div>
                  <p className="text-sm font-medium">{t.title}</p>
                  <p className="text-xs text-muted font-mono mt-1">{t.path.join(" -> ")}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`pill ${t.risk_score > 0.6 ? "pill-critical" : t.risk_score > 0.35 ? "pill-warning" : "pill-success"}`}>
                    risk {t.risk_score.toFixed(2)}
                  </span>
                  <span className="pill pill-muted">{Math.round(t.probability * 100)}% probability</span>
                </div>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 border-t border-border pt-4 space-y-5">
                  <div>
                    <p className="text-xs text-muted uppercase tracking-wide mb-2">Evidence</p>
                    <ul className="space-y-1">
                      {t.evidence.map((e, i) => (
                        <li key={i} className="text-sm text-ink/90">- {e}</li>
                      ))}
                    </ul>
                    <p className="text-xs text-muted uppercase tracking-wide mt-4 mb-1">Affected assets</p>
                    <div className="flex gap-2 flex-wrap">
                      {t.affected_assets.map((a) => (
                        <span key={a} className="pill pill-muted font-mono">{a}</span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-muted uppercase tracking-wide mb-2">Recommended defenses</p>
                    {recsLoading && !threatRecs && <p className="text-sm text-muted">Comparing mitigation strategies...</p>}
                    {threatRecs && threatRecs.length === 0 && (
                      <p className="text-sm text-muted">No candidate actions apply to this asset.</p>
                    )}
                    {threatRecs && threatRecs.length > 0 && (
                      <div className="space-y-2">
                        {threatRecs.map((rec, i) => (
                          <div
                            key={rec.action}
                            className={`px-3 py-3 rounded-md border ${i === 0 ? "border-accent/40 bg-accent/5" : "border-border"}`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {i === 0 && <span className="pill pill-success">top pick</span>}
                                <span className="text-sm font-medium">{rec.action}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="pill pill-muted">score {rec.score.toFixed(2)}</span>
                                <button
                                  onClick={() => apply(t, rec)}
                                  className="text-xs px-2 py-1 rounded border border-border hover:border-accent/40 transition"
                                >
                                  Mark as applied
                                </button>
                              </div>
                            </div>
                            <p className="text-xs text-muted mt-2">{rec.rationale}</p>
                            <div className="flex gap-2 mt-2">
                              <span className="pill pill-success">-{Math.round(rec.risk_reduction * 100)}% risk</span>
                              <span className="pill pill-warning">{Math.round(rec.operational_cost * 100)}% op. cost</span>
                              <span className="pill pill-muted">{Math.round(rec.historical_success * 100)}% historical success</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
