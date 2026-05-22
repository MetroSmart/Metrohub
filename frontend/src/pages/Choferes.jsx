import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const ESTADO_STYLE = {
  activo:         { bg: "#EAF3DE", color: "#27500A" },
  suspendido:     { bg: "#FCEBEB", color: "#791F1F" },
  licencia_medica:{ bg: "#FAEEDA", color: "#633806" },
  vacaciones:     { bg: "#E6F1FB", color: "#0C447C" },
  inactivo:       { bg: "#f0f0f0", color: "#888"    },
};

export default function Choferes({ user, onNav, onLogout }) {
  const [choferes, setChoferes] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [filtroEstado, setFiltro] = useState("");

  useEffect(() => {
    const url = filtroEstado ? `/api/choferes?estado=${filtroEstado}` : "/api/choferes";
    setLoading(true);
    api.get(url)
      .then(data => { setChoferes(data); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, [filtroEstado]);

  const hoy = new Date();
  const diasParaVencer = (fechaStr) => {
    const diff = new Date(fechaStr) - hoy;
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="choferes" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Personal</div>
            <h1 style={styles.pageTitle}>Choferes</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* Filtro */}
        <div>
          <select value={filtroEstado} onChange={e => setFiltro(e.target.value)} style={styles.select}>
            <option value="">Todos los estados</option>
            <option value="activo">Activo</option>
            <option value="suspendido">Suspendido</option>
            <option value="licencia_medica">Licencia médica</option>
            <option value="vacaciones">Vacaciones</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </div>

        {loading && <div style={styles.empty}>Cargando choferes…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {!loading && !error && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Chofer","DNI","Licencia","Tipo","Vence licencia","Vence certif.","Estado"].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {choferes.map(c => {
                  const est = ESTADO_STYLE[c.estado] ?? ESTADO_STYLE.inactivo;
                  const diasLic   = diasParaVencer(c.fec_vence_licencia);
                  const diasCert  = diasParaVencer(c.fec_vence_certif_prot);
                  const licAlerta = diasLic  <= 30;
                  const certAlerta= diasCert <= 30;
                  return (
                    <tr key={c.id} style={{ background: (licAlerta || certAlerta) ? "#fffdf5" : "transparent" }}>
                      <td style={styles.td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                          <span style={styles.avatar}>
                            {c.nombres[0]}{c.apellidos[0]}
                          </span>
                          <div>
                            <div style={{ fontWeight: 500 }}>{c.nombres} {c.apellidos}</div>
                          </div>
                        </div>
                      </td>
                      <td style={styles.td}>{c.dni}</td>
                      <td style={styles.td}>{c.numero_licencia}</td>
                      <td style={styles.td}>{c.tipo_licencia}</td>
                      <td style={styles.td}>
                        <span style={{ color: licAlerta ? "#791F1F" : "#222", fontWeight: licAlerta ? 600 : 400 }}>
                          {c.fec_vence_licencia}
                          {licAlerta && <span style={styles.alertBadge}>{diasLic < 0 ? "VENCIDA" : `${diasLic}d`}</span>}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ color: certAlerta ? "#791F1F" : "#222", fontWeight: certAlerta ? 600 : 400 }}>
                          {c.fec_vence_certif_prot}
                          {certAlerta && <span style={styles.alertBadge}>{diasCert < 0 ? "VENCIDA" : `${diasCert}d`}</span>}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: est.bg, color: est.color }}>
                          {c.estado.replace("_", " ")}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{choferes.length} choferes</div>
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
  select:    { fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#222", outline: "none" },
  tableWrap: { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:     { width: "100%", borderCollapse: "collapse" },
  th:        { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:        { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:       { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  avatar:    { width: 30, height: 30, borderRadius: "50%", background: "#B5D4F4", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: "#0C447C", flexShrink: 0 },
  alertBadge:{ marginLeft: 6, background: "#FCEBEB", color: "#791F1F", fontSize: 10, fontWeight: 700, padding: "1px 6px", borderRadius: 4 },
  footer:    { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:     { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:  { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
};
