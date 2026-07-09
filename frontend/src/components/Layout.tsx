import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import RouteTransition from "./RouteTransition";

export default function Layout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#0B0F19]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <RouteTransition>
            <Outlet />
          </RouteTransition>
        </div>
      </main>
    </div>
  );
}


