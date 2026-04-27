import { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Grilla from "./pages/Grilla";

export default function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
    setPage("dashboard");
  };

  const handleLogout = () => {
    setUser(null);
    setPage("login");
  };

  if (page === "login") return <Login onLogin={handleLogin} />;
  if (page === "grilla") return <Grilla user={user} onNav={setPage} onLogout={handleLogout} />;
  return <Dashboard user={user} onNav={setPage} onLogout={handleLogout} />;
}