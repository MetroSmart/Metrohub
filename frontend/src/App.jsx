import { useEffect, useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Grilla from "./pages/Grilla";
import Rutas from "./pages/Rutas";
import Choferes from "./pages/Choferes";
import Reportes from "./pages/Reportes";
import Buses from "./pages/Buses";
import Usuarios from "./pages/Usuarios";
import Concesionarios from "./pages/Concesionarios";
import MisRutas from "./pages/MisRutas";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [page, setPage]                     = useState("login");
  const [user, setUser]                     = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const token = localStorage.getItem("metrohub_access_token");
      if (!token) { setCheckingSession(false); return; }
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
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
          name: `${data.nombre} ${data.apellidos || ""}`.trim() || data.email.split("@")[0],
          chofer_id: data.chofer_id ?? null,
        });
        setPage(data.rol === "chofer" ? "mis-rutas" : "dashboard");
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
    setPage(userData.role === "chofer" ? "mis-rutas" : "dashboard");
  };
  const handleLogout = () => {
    localStorage.removeItem("metrohub_access_token");
    setUser(null);
    setPage("login");
  };

  if (checkingSession) {
    return (
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", background: "#042C53",
        fontFamily: "'DM Sans',sans-serif", color: "#85B7EB", fontSize: 15,
      }}>
        Cargando MetroHub…
      </div>
    );
  }

  const props = { user, onNav: setPage, onLogout: handleLogout };

  if (page === "login")          return <Login onLogin={handleLogin} />;
  if (page === "mis-rutas")      return <MisRutas       {...props} />;
  if (page === "grilla")         return <Grilla         {...props} />;
  if (page === "rutas")          return <Rutas          {...props} />;
  if (page === "choferes")       return <Choferes       {...props} />;
  if (page === "reportes")       return <Reportes       {...props} />;
  if (page === "buses")          return <Buses          {...props} />;
  if (page === "usuarios")       return <Usuarios       {...props} />;
  if (page === "concesionarios") return <Concesionarios {...props} />;
  return <Dashboard {...props} />;
}
