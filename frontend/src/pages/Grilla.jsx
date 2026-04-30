import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TURNO_STYLE = {
  manana: { background: "#E6F1FB", color: "#0C447C" },
  tarde:  { background: "#FAEEDA", color: "#633806" },
  noche:  { background: "#F3E6FB", color: "#4A0C7C" },
};
const TURNO_LABEL = { manana: "Mañana", tarde: "Tarde", noche: "Noche" };

const SEV_STYLE = {
  alta:   { background: "#FCEBEB", color: "#791F1F", border: "1px solid #F7C1C1" },
  media:  { background: "#FAEEDA", color: "#633806", border: "1px solid #F0D1A0" },
  baja:   { background: "#FFF8E1", color: "#7A5800", border: "1px solid #F0D87A" },
  critica:{ background: "#F5E6FF", color: "#5A0B8E", border: "1px solid #D6B3F7" },
};

export default function Grilla({ user, onNav, onLogout }) {
  const [horarios, setHorarios] = useState([]);
  const [rutas, setRutas]       = useState([]);
  const [rutaId, setRutaId]     = useState("");
  const [fecha, setFecha]       = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading]   = useState(true);
  const [saved, setSaved]       = useState(false);
  const [resolving, setResolving] = useState(null);

  useEffect(() => {
    api.get("/api/rutas?solo_activas=true").then(setRutas).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (fecha)  params.set("fecha",   fecha);
    if (rutaId) params.set("ruta_id", rutaId);
    api.get(`/api/horarios?${params}`)
      .then(d => { setHorarios(d.horarios ?? []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [fecha, rutaId]);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const handleResolver = async (conflictoId, horarioId) => {
    setResolving(conflictoId);
    try {
      await api.patch(`/api/conflictos/${conflictoId}/resolver`);
      setHorarios(prev =>
        prev.map(h => h.id === horarioId ? { ...h, conflicto: null } : h)
      );
    } catch {
      alert("No se pudo resolver. Verifica que tengas rol de Administrador ATU.");
    } finally {
      setResolving(null);
    }
  };

  const conflictCount = horarios.filter(h => h.conflicto).length;

  return (
    <div style={styles.layout}>
      <Sidebar active="grilla" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        {/* Topbar */}
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Programación</div>
            <h1 style={styles.pageTitle}>Grilla de horarios</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* Controles */}
        <div style={styles.controls}>
          <select value={rutaId} onChange={e => setRutaId(e.target.value)} style={styles.select}>
            <option value="">Todas las rutas</option>
            {rutas.map(r => (
              <option key={r.id} value={r.id}>{r.codigo} — {r.nombre}</option>
            ))}
          </select>
          <input
            type="date" value={fecha}
            onChange={e => setFecha(e.target.value)}
            style={styles.select}
          />
          <button style={styles.btnSecondary} onClick={handleSave}>
            {saved ? "✓ Guardado" : "Guardar borrador"}
          </button>
          <button style={styles.btnPrimary}>
            Aprobar programación
          </button>
          {conflictCount > 0 && (
            <span style={styles.conflictBadge}>
              {conflictCount} conflicto{conflictCount > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Tabla */}
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                {["Hora salida", "Ruta", "Chofer", "Turno", "Duración", "Estado"].map(h => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={6} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                    Cargando…
                  </td>
                </tr>
              )}
              {!loading && horarios.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                    Sin horarios para esta fecha / ruta.
                  </td>
                </tr>
              )}
              {!loading && horarios.map(h => {
                const tieneConflicto = !!h.conflicto;
                const rowStyle = tieneConflicto ? styles.rowConflicto : {};
                return (
                  <tr key={h.id} style={rowStyle}>
                    {/* Hora salida */}
                    <td style={styles.td}>
                      <strong style={{ fontFamily: "'Space Mono',monospace", fontSize: 13 }}>
                        {h.hora_salida}
                      </strong>
                    </td>

                    {/* Ruta */}
                    <td style={styles.td}>
                      {rutas.find(r => r.id === h.ruta_id)?.codigo ?? `Ruta #${h.ruta_id}`}
                    </td>

                    {/* Chofer */}
                    <td style={styles.td}>
                      {h.chofer
                        ? (
                          <div style={styles.choferBadge}>
                            <span style={styles.avatar}>
                              {h.chofer.nombre.split(" ").map(w => w[0]).slice(0, 2).join("")}
                            </span>
                            <span>{h.chofer.nombre}</span>
                          </div>
                        )
                        : <span style={{ color: "#bbb", fontSize: 12 }}>Sin asignar</span>
                      }
                    </td>

                    {/* Turno */}
                    <td style={styles.td}>
                      <span style={{ ...styles.tag, ...(TURNO_STYLE[h.turno] ?? {}) }}>
                        {TURNO_LABEL[h.turno] ?? h.turno}
                      </span>
                    </td>

                    {/* Duración */}
                    <td style={styles.td}>{h.duracion_est_min} min</td>

                    {/* Estado */}
                    <td style={styles.td}>
                      {tieneConflicto ? (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                            <span style={{ ...styles.tag, ...(SEV_STYLE[h.conflicto.severidad] ?? SEV_STYLE.media) }}>
                              Conflicto
                            </span>
                            <span style={{ fontSize: 11, color: "#9B2C2C" }}>
                              {h.conflicto.tipo.replace(/_/g, " ")}
                            </span>
                          </div>
                          <div style={styles.conflictDesc}>{h.conflicto.descripcion}</div>
                          {user?.role === "admin_atu" && (
                            <button
                              style={styles.resolveBtn}
                              disabled={resolving === h.conflicto.id}
                              onClick={() => handleResolver(h.conflicto.id, h.id)}
                            >
                              {resolving === h.conflicto.id ? "Resolviendo…" : "Resolver"}
                            </button>
                          )}
                        </div>
                      ) : (
                        <span style={{
                          ...styles.tag,
                          background: h.activo ? "#EAF3DE" : "#f0f0f0",
                          color:      h.activo ? "#27500A" : "#888",
                        }}>
                          {h.activo ? "Activo" : "Inactivo"}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {!loading && horarios.length > 0 && (
          <div style={styles.successBanner}>
            {horarios.length} horario{horarios.length > 1 ? "s" : ""} para {fecha}.{" "}
            {conflictCount > 0
              ? `${conflictCount} con conflicto activo.`
              : "Sin conflictos."}
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
  badge: {
    background: "#185FA5", color: "#E6F1FB",
    fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500,
    padding: "5px 12px", borderRadius: 20,
  },
  controls: { display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" },
  select: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "8px 12px",
    borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#222", outline: "none",
  },
  btnSecondary: {
    padding: "8px 16px", borderRadius: 8, border: "1px solid #ddd", background: "#fff",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444", cursor: "pointer",
  },
  btnPrimary: {
    padding: "8px 18px", borderRadius: 8, border: "none", background: "#185FA5",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer",
  },
  conflictBadge: {
    background: "#FCEBEB", color: "#791F1F", border: "1px solid #F7C1C1",
    fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 600,
    padding: "4px 12px", borderRadius: 20,
  },
  tableWrap: {
    background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden",
  },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888",
    padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left",
    background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px",
  },
  td: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222",
    padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "top",
  },
  rowConflicto: { background: "#fff9f9" },
  choferBadge: { display: "inline-flex", alignItems: "center", gap: 7 },
  avatar: {
    width: 24, height: 24, borderRadius: "50%", background: "#B5D4F4",
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    fontSize: 10, fontWeight: 600, color: "#0C447C", flexShrink: 0,
  },
  tag: {
    display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500,
  },
  conflictDesc: {
    fontSize: 11, color: "#9B2C2C", lineHeight: 1.4, maxWidth: 340,
  },
  resolveBtn: {
    padding: "3px 10px", borderRadius: 6, border: "1px solid #F7C1C1",
    background: "#FCEBEB", color: "#791F1F", fontSize: 11,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif", width: "fit-content",
  },
  successBanner: {
    background: "#EAF3DE", border: "0.5px solid #C0DD97", borderRadius: 8,
    padding: "11px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#27500A",
  },
};
