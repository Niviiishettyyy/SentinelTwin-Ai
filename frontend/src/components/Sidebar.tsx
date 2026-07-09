import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Network, PlaySquare, ShieldAlert, MessageSquareText,
  FileBarChart2, Settings as SettingsIcon, LogOut,
} from "lucide-react";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/twin", label: "Digital Twin", icon: Network },
  { to: "/simulation", label: "Simulation Center", icon: PlaySquare },
  { to: "/threats", label: "Threats", icon: ShieldAlert },
  { to: "/assistant", label: "Assistant", icon: MessageSquareText },
  { to: "/reports", label: "Reports", icon: FileBarChart2 },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem("st_token");
    navigate("/login");
  };

  return (
    <aside className="w-60 shrink-0 bg-[#0D1220] border-r border-[#1F2937] flex flex-col">
      <div className="px-5 py-5 border-b border-[#1F2937]">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#2DD4BF] shadow-[0_0_8px_2px_rgba(45,212,191,0.6)]" />
          <span className="font-semibold tracking-tight text-[15px]">SentinelTwin</span>
        </div>
        <p className="text-xs text-muted mt-1">Predict. Simulate. Learn. Protect.</p>
      </div>
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `navlink relative group ${
                isActive
                  ? "text-[#2DD4BF] border border-[#2DD4BF]/30 bg-[#2DD4BF]/10"
                  : "text-muted border border-transparent hover:text-ink hover:bg-white/5"
              }`
            }
          >
            <span
              className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-r transition-all duration-300 ease-out ${
                "opacity-0 group-hover:opacity-100 bg-[#2DD4BF]/30"
              }`}
            />
            <span
              className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-r transition-all duration-300 ease-out ${
                "opacity-0 bg-[#2DD4BF]"
              }`}
              style={{ opacity: window.location.pathname === to ? 1 : undefined }}
            />
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-4 border-t border-[#1F2937] text-xs text-muted font-mono flex items-center justify-between">
        <span>
          twin status: <span className="text-success">live-replay</span>
        </span>
        <button
          onClick={logout}
          title="Log out"
          className="text-muted hover:text-[#F43F5E] transition hover:scale-[1.02]"
        >
          <LogOut size={14} />
        </button>
      </div>
    </aside>
  );
}

