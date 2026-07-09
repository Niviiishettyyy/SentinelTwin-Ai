import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api/client";

export default function Login() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async () => {
    if (!username || !password) {
      setError("Enter a username and password.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = mode === "login" ? await login(username, password) : await register(username, password);
      localStorage.setItem("st_token", res.access_token);
      navigate("/");
    } catch (e: any) {
      setError(
        mode === "login"
          ? "Login failed. Check your username and password, or register a new account."
          : "Registration failed. That username may already be taken."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-base">
      <div className="card w-full max-w-sm p-6">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_2px_rgba(56,189,248,0.6)]" />
          <span className="font-semibold tracking-tight">SentinelTwin</span>
        </div>
        <p className="text-xs text-muted mb-6">Predict. Simulate. Learn. Protect.</p>

        <div className="flex gap-1 mb-5 bg-raised rounded-md p-1 text-sm">
          <button
            onClick={() => setMode("login")}
            className={`flex-1 py-1.5 rounded ${mode === "login" ? "bg-accent/15 text-accent" : "text-muted"}`}
          >
            Log in
          </button>
          <button
            onClick={() => setMode("register")}
            className={`flex-1 py-1.5 rounded ${mode === "register" ? "bg-accent/15 text-accent" : "text-muted"}`}
          >
            Register
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-muted">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full mt-1 bg-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/50"
            />
          </div>
          <div>
            <label className="text-xs text-muted">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              className="w-full mt-1 bg-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/50"
            />
          </div>
        </div>

        {error && <p className="text-critical text-xs mt-3">{error}</p>}

        <button className="btn-primary w-full mt-5" onClick={submit} disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
        </button>
      </div>
    </div>
  );
}
