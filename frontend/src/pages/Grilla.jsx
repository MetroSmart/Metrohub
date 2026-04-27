import { useState } from "react";
import Sidebar from "../components/Sidebar";

const SLOTS_INICIAL = [
  { id: 1, hora: "05:30", unidad: "U-043", chofer: "C-012", iniciales: "RM", estacion: "Naranjal",  estado: "ok",       turno: "Mañana" },
  { id: 2, hora: "06:00", unidad: "U-051", chofer: "C-028", iniciales: "JC", estacion: "Naranjal",  estado: "ok",       turno: "Mañana" },
  { id: 3, hora: "08:00", unidad: "U-067", chofer: "C-047", iniciales: "LC", estacion: "Comas",     estado: "conflict", turno: "Mañana" },
  { id: 4, hora: "10:30", unidad: "—",     chofer: "",      iniciales: "",   estacion: "Naranjal",  estado: "empty",    turno: "Tarde"  },
  { id: 5, hora: "14:00", unidad: "U-089", chofer: "C-055", iniciales: "AP", estacion: "Naranjal",  estado: "ok",       turno: "Tarde"  },
  { id: 6, hora: "17:00", unidad: "U-102", chofer: "C-061", iniciales: "MG", estacion: "Matellini", estado: "ok",       turno: "Tarde"  },
];

const STATUS_LABEL = { ok: "Confirmado", conflict: "Conflicto", empty: "Pendiente" };
const STATUS_STYLE = {
  ok:       { background: "#EAF3DE", color: "#27500A" },
  conflict: { background: "#FCEBEB", color: "#791F1F" },
  empty:    { background: "#f0f0f0", color: "#888"    },
};

export default function Grilla({ user, onNav, onLogout }) {
  const [slots, setSlots] = useState(SLOTS_INICIAL);
  const [ruta, setRuta] = useState("rt-a");
  const [semana, setSemana] = useState("sem18");
  const [saved, setSaved] = useState(false);

  const conflicts = slots.filter(s => s.estado === "conflict");

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const resolveConflict = (id) => {
    setSlots(prev => prev.map(s => s.id === id ? { ...s, estado: "ok" } : s));
  };

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
            {user?.role === "admin" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* Controles */}
        <div style={styles.controls}>
          <select value={ruta} onChange={e => setRuta(e.target.value)} style={styles.select}>
            <option value="rt-a">Ruta A — Naranjal → Matellini</option>
            <option value="rt-b">Ruta B — Naranjal → Chorrillos</option>
            <option value="exp">Expreso 1</option>
            <option value="rt-c">Ruta C — Comas → Barranco</option>
          </select>
          <select value={semana} onChange={e => setSemana(e.target.value)} style={styles.select}>
            <option value="sem18">Semana 18 (28 abr – 4 may)</option>
            <option value="sem19">Semana 19 (5 – 11 may)</option>
            <option value="sem20">Semana 20 (12 – 18 may)</option>
          </select>
          <button style={styles.btnSecondary} onClick={handleSave}>
            {saved ? "✓ Guardado" : "Guardar borrador"}
          </button>
          <button style={styles.btnPrimary}>
            Aprobar programación
          </button>
        </div>

        {/* Tabla grilla */}
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                {["Hora salida","Unidad","Chofer","Estación inicio","Turno","Estado",""].map(h => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {slots.map(slot => (
                <tr key={slot.id} style={{ background: slot.estado === "conflict" ? "#fff8f8" : "transparent" }}>
                  <td style={styles.td}>
                    <strong style={{ fontFamily: "'Space Mono',monospace", fontSize: 13 }}>
                      {slot.hora}
                    </strong>
                  </td>
                  <td style={styles.td}>{slot.unidad}</td>
                  <td style={styles.td}>
                    {slot.chofer ? (
                      <span style={styles.choferBadge}>
                        <span style={styles.avatar}>{slot.iniciales}</span>
                        {slot.chofer}
                      </span>
                    ) : (
                      <span style={{ color: "#bbb", fontSize: 12 }}>Sin asignar</span>
                    )}
                  </td>
                  <td style={styles.td}>{slot.estacion}</td>
                  <td style={styles.td}>
                    <span style={{
                      ...styles.turnoTag,
                      background: slot.turno === "Mañana" ? "#E6F1FB" : "#FAEEDA",
                      color: slot.turno === "Mañana" ? "#0C447C" : "#633806",
                    }}>
                      {slot.turno}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <span style={{ ...styles.statusTag, ...STATUS_STYLE[slot.estado] }}>
                      {STATUS_LABEL[slot.estado]}
                    </span>
                  </td>
                  <td style={styles.td}>
                    {slot.estado === "conflict" && (
                      <button style={styles.resolveBtn} onClick={() => resolveConflict(slot.id)}>
                        Resolver
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Banner conflictos */}
        {conflicts.length > 0 && (
          <div style={styles.conflictBanner}>
            <strong>{conflicts.length} conflicto{conflicts.length > 1 ? "s" : ""} detectado{conflicts.length > 1 ? "s" : ""}:</strong>
            {" "}Chofer C-047 tiene turno solapado con RT-C a las 08:00h.
            Revisa disponibilidad antes de confirmar.
          </div>
        )}

        {conflicts.length === 0 && (
          <div style={styles.successBanner}>
            Sin conflictos. La programación está lista para aprobar.
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  layout: { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main: { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 18, overflow: "auto" },
  topbar: { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  breadcrumb: { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3 },
  pageTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge: {
    background: "#185FA5", color: "#E6F1FB",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 11, fontWeight: 500,
    padding: "5px 12px", borderRadius: 20,
  },
  controls: { display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" },
  select: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, padding: "8px 12px",
    borderRadius: 8, border: "1px solid #ddd",
    background: "#fff", color: "#222", outline: "none",
  },
  btnSecondary: {
    padding: "8px 16px", borderRadius: 8,
    border: "1px solid #ddd", background: "#fff",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, color: "#444", cursor: "pointer",
  },
  btnPrimary: {
    padding: "8px 18px", borderRadius: 8,
    border: "none", background: "#185FA5",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer",
  },
  tableWrap: {
    background: "#fff",
    border: "0.5px solid #e8e8e8",
    borderRadius: 10,
    overflow: "hidden",
  },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 11, fontWeight: 500, color: "#888",
    padding: "10px 14px",
    borderBottom: "1px solid #f0f0f0",
    textAlign: "left",
    background: "#fafafa",
    textTransform: "uppercase", letterSpacing: "0.4px",
  },
  td: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, color: "#222",
    padding: "11px 14px",
    borderBottom: "0.5px solid #f4f4f4",
    verticalAlign: "middle",
  },
  choferBadge: { display: "inline-flex", alignItems: "center", gap: 7 },
  avatar: {
    width: 24, height: 24, borderRadius: "50%",
    background: "#B5D4F4",
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    fontSize: 10, fontWeight: 600, color: "#0C447C",
    flexShrink: 0,
  },
  statusTag: {
    display: "inline-block",
    padding: "3px 9px",
    borderRadius: 4,
    fontSize: 11, fontWeight: 500,
  },
  turnoTag: {
    display: "inline-block",
    padding: "3px 9px",
    borderRadius: 4,
    fontSize: 11, fontWeight: 500,
  },
  resolveBtn: {
    padding: "4px 10px",
    borderRadius: 6,
    border: "1px solid #F7C1C1",
    background: "#FCEBEB",
    color: "#791F1F",
    fontSize: 11,
    cursor: "pointer",
    fontFamily: "'DM Sans',sans-serif",
  },
  conflictBanner: {
    background: "#FCEBEB",
    border: "0.5px solid #F7C1C1",
    borderRadius: 8,
    padding: "11px 16px",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, color: "#791F1F",
  },
  successBanner: {
    background: "#EAF3DE",
    border: "0.5px solid #C0DD97",
    borderRadius: 8,
    padding: "11px 16px",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, color: "#27500A",
  },
};