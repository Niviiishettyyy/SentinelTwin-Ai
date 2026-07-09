# SentinelTwin AI — Frontend

React + TypeScript + Tailwind + React Flow + Recharts frontend implementing
the pages described in the project artifact (Dashboard, Digital Twin,
Simulation Center, Threats, Assistant, Reports, Settings).

## Setup

```bash
npm install
npm run dev
```

Runs at http://localhost:5173 and proxies `/api/*` to the backend at
http://localhost:8000 (see `vite.config.ts`).

## Auth note

This scaffold expects a JWT in `localStorage.st_token`. Wire up a login
page against `POST /api/auth/login` (see `src/api/client.ts -> login()`)
and store the returned `access_token` there before hitting the other
pages — otherwise API calls will 401.

## Design tokens

Dark, operational security-product palette defined in `tailwind.config.js`:
navy background (#0B1220), cyan accent (#38BDF8), with amber/rose/green
for warning/critical/success states. Inter for UI text, JetBrains Mono for
scores, IDs, and technical data (see Section 10/17 of the artifact —
"calm, premium, operational").
