import { useEffect, useState } from "react";
import { api } from "../api/client";

const DEFAULT_PREFS = {
  notify_critical: "true",
  notify_weekly_report: "true",
  theme: "dark",
};

export default function Settings() {
  const [prefs, setPrefs] = useState<Record<string, string>>(DEFAULT_PREFS);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    api.get("/settings/preferences").then((r) => {
      if (Object.keys(r.data).length > 0) setPrefs({ ...DEFAULT_PREFS, ...r.data });
    }).catch(() => {});
  }, []);

  const save = async (key: string, value: string) => {
    setPrefs((p) => ({ ...p, [key]: value }));
    try {
      await api.put(`/settings/preferences/${key}`, null, { params: { value } });
      setStatus("Saved");
      setTimeout(() => setStatus(null), 1500);
    } catch {
      setStatus("Could not save — is the backend running and are you logged in?");
    }
  };

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="text-sm text-muted mt-1">Preferences, notifications, and account options.</p>
      </header>

      <div className="card p-5 max-w-lg space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Notify on critical threats</p>
            <p className="text-xs text-muted">Get alerted immediately when a critical-risk node is flagged.</p>
          </div>
          <input
            type="checkbox"
            checked={prefs.notify_critical === "true"}
            onChange={(e) => save("notify_critical", String(e.target.checked))}
            className="w-4 h-4 accent-accent"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Weekly executive report</p>
            <p className="text-xs text-muted">Send a summary report every week.</p>
          </div>
          <input
            type="checkbox"
            checked={prefs.notify_weekly_report === "true"}
            onChange={(e) => save("notify_weekly_report", String(e.target.checked))}
            className="w-4 h-4 accent-accent"
          />
        </div>

        {status && <p className="text-xs text-accent">{status}</p>}
      </div>
    </div>
  );
}
