import { useEffect, useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Grilla from "./pages/Grilla";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const token = localStorage.getItem("metrohub_access_token");
      if (!token) {
        setCheckingSession(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          localStorage.removeItem("metrohub_access_token");
          setCheckingSession(false);
          return;
        }

        const data = await response.json();
        setUser({
          email: data.email,
          role: data.rol,
          name: data.email.split("@")[0],
        });
        setPage("dashboard");
      } catch {
        localStorage.removeItem("metrohub_access_token");
      } finally {
        setCheckingSession(false);
      }
    };

    restoreSession();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("metrohub_access_token");
    setUser(null);
    setPage("login");
  };

  if (checkingSession) return null;

  if (page === "login") return <Login onLogin={handleLogin} />;
  if (page === "grilla") return <Grilla user={user} onNav={setPage} onLogout={handleLogout} />;
  return <Dashboard user={user} onNav={setPage} onLogout={handleLogout} />;
}