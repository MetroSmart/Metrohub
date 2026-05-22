import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TIPO_COLOR = {
  regular:  { bg: "#E6F1FB", color: "#0C447C" },
  expreso:  { bg: "#EAF3DE", color: "#27500A" },
  nocturna: { bg: "#F3E6FB", color: "#4A0C7C" },
};

export default function Rutas({ user, onNav, onLogout }) {
  const [rutas, setRutas]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    api.get("/api/rutas")
      .then(data => { setRutas(data); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, []);

  return (
    <div style={styles.layout}>
      <Sidebar active="rutas" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Catálogo operativo</div>
            <h1 style={styles.pageTitle}>Rutas y Estaciones</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {loading && <div style={styles.empty}>Cargando rutas…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {!loading && !error && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Código","Nombre","Tipo","Horario","Frecuencia","Estado"].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rutas.map(r => {
                  const tc = TIPO_COLOR[r.tipo] ?? { bg: "#f0f0f0", color: "#444" };
                  return (
                    <tr key={r.id}>
                      <td style={styles.td}>
                        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: 12, fontWeight: 600 }}>
                          {r.codigo}
                        </span>
                      </td>
                      <td style={styles.td}>{r.nombre}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: tc.bg, color: tc.color }}>
                          {r.tipo}
                        </span>
                      </td>
                      <td style={styles.td}>
                        {r.hora_inicio} – {r.hora_fin}
                      </td>
                      <td style={styles.td}>
                        Cada {r.frecuencia_min} min
                      </td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.tag,
                          background: r.activa ? "#EAF3DE" : "#f0f0f0",
                          color:      r.activa ? "#27500A" : "#888",
                        }}>
                          {r.activa ? "Activa" : "Inactiva"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{rutas.length} rutas en total</div>
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  layout:    { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main:      { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 18, overflow: "auto" },
  topbar:    { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  breadcrumb:{ fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3 },
  pageTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge:     { background: "#185FA5", color: "#E6F1FB", fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, padding: "5px 12px", borderRadius: 20 },
  tableWrap: { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:     { width: "100%", borderCollapse: "collapse" },
  th:        { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:        { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:       { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  footer:    { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:     { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:  { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
};
