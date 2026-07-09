import { Navigate } from "react-router-dom";

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("st_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
