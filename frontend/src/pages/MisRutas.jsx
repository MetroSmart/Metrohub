import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TURNO_STYLE = {
  manana: { background: "#E6F1FB", color: "#0C447C" },
  tarde:  { background: "#FAEEDA", color: "#633806" },
  noche:  { background: "#F3E6FB", color: "#4A0C7C" },
};
const TURNO_LABEL = { manana: "Mañana", tarde: "Tarde", noche: "Noche" };

const ESTADO_STYLE = {
  confirmada: { background: "#EAF3DE", color: "#27500A" },
  propuesta:  { background: "#FAEEDA", color: "#633806" },
};

export default function MisRutas({ user, onNav, onLogout }) {
  const [fecha, setFecha] = useState(new Date().toISOString().slice(0, 10));
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    api.get(`/api/choferes/me/asignaciones?fecha=${fecha}`)
      .then(setData)
      .catch(err => setError(err.message || "No se pudieron cargar tus rutas"))
      .finally(() => setLoading(false));
  }, [fecha]);

  const fechaLabel = new Date(fecha + "T12:00:00").toLocaleDateString("es-PE", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  const asignaciones = data?.asignaciones ?? [];
  const siguiente = asignaciones.find(a => a.es_siguiente);

  return (
    <div style={styles.layout}>
      <Sidebar active="mis-rutas" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.dateStr}>{fechaLabel}</div>
            <h1 style={styles.pageTitle}>Mis rutas asignadas</h1>
            <p style={styles.subtitle}>
              {data?.chofer_nombre
                ? `Chofer: ${data.chofer_nombre}`
                : "Consulta tu programación del día"}
            </p>
          </div>
          <div style={styles.topActions}>
            <input
              type="date"
              value={fecha}
              onChange={e => setFecha(e.target.value)}
              style={styles.dateInput}
            />
            <div style={styles.badge}>Chofer</div>
          </div>
        </div>

        {error && <div style={styles.errorBox}>{error}</div>}

        {loading ? (
          <div style={styles.empty}>Cargando asignaciones…</div>
        ) : asignaciones.length === 0 ? (
          <div style={styles.panelCard}>
            <div style={styles.empty}>
              No tienes rutas asignadas para esta fecha.
            </div>
          </div>
        ) : (
          <>
            {siguiente && (
              <section style={styles.panelCard}>
                <div style={styles.sectionHeader}>
                  <div>
                    <div style={styles.sectionLabel}>Próximo servicio</div>
                    <div style={styles.sectionTitle}>
                      Ruta {siguiente.ruta.codigo} — {siguiente.ruta.nombre}
                    </div>
                  </div>
                  <div style={styles.timeBig}>{siguiente.horario.hora_salida}</div>
                </div>

                <div style={styles.metaRow}>
                  <span style={{ ...styles.chip, ...TURNO_STYLE[siguiente.horario.turno] }}>
                    {TURNO_LABEL[siguiente.horario.turno]}
                  </span>
                  <span style={{ ...styles.chip, ...ESTADO_STYLE[siguiente.estado] }}>
                    {siguiente.estado}
                  </span>
                  {siguiente.bus_placa && (
                    <span style={styles.chipMuted}>Bus {siguiente.bus_placa}</span>
                  )}
                  <span style={styles.chipMuted}>
                    {siguiente.horario.duracion_est_min} min
                  </span>
                </div>

                <div style={styles.stationsTitle}>Estaciones de la ruta</div>
                <div style={styles.stationsList}>
                  {(siguiente.estaciones ?? []).map((est, idx) => (
                    <div key={`${est.estacion_id}-${est.orden}`} style={styles.stationItem}>
                      <div style={styles.stationTrack}>
                        <div style={{
                          ...styles.stationDot,
                          background: idx === 0 ? "#378ADD" : "#85B7EB",
                        }} />
                        {idx < (siguiente.estaciones?.length ?? 0) - 1 && (
                          <div style={styles.stationLine} />
                        )}
                      </div>
                      <div style={styles.stationBody}>
                        <div style={styles.stationName}>
                          <span style={styles.stationCode}>{est.codigo}</span>
                          {est.nombre}
                        </div>
                        <div style={styles.stationMeta}>
                          Parada {est.orden}
                          {est.tiempo_est_min != null ? ` · +${est.tiempo_est_min} min` : ""}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section style={styles.panelCard}>
              <div style={styles.panelTitle}>
                Todos mis servicios ({asignaciones.length})
              </div>
              <div style={styles.tableWrap}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Hora</th>
                      <th style={styles.th}>Ruta</th>
                      <th style={styles.th}>Turno</th>
                      <th style={styles.th}>Bus</th>
                      <th style={styles.th}>Estado</th>
                      <th style={styles.th}>Paradas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {asignaciones.map(asig => (
                      <tr
                        key={asig.asignacion_id}
                        style={asig.es_siguiente ? styles.rowHighlight : undefined}
                      >
                        <td style={styles.tdStrong}>{asig.horario.hora_salida}</td>
                        <td style={styles.td}>
                          <div style={styles.routeCode}>{asig.ruta.codigo}</div>
                          <div style={styles.routeName}>{asig.ruta.nombre}</div>
                        </td>
                        <td style={styles.td}>
                          <span style={{ ...styles.chip, ...TURNO_STYLE[asig.horario.turno] }}>
                            {TURNO_LABEL[asig.horario.turno]}
                          </span>
                        </td>
                        <td style={styles.td}>{asig.bus_placa ?? "—"}</td>
                        <td style={styles.td}>
                          <span style={{ ...styles.chip, ...ESTADO_STYLE[asig.estado] }}>
                            {asig.estado}
                          </span>
                        </td>
                        <td style={styles.td}>{asig.estaciones?.length ?? 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

const styles = {
  layout: { display: "flex", minHeight: "100vh", background: "#F4F7FB" },
  main:   { flex: 1, padding: "28px 32px", overflow: "auto" },
  topbar: {
    display: "flex", justifyContent: "space-between", alignItems: "flex-start",
    gap: 16, marginBottom: 24, flexWrap: "wrap",
  },
  dateStr:   { fontSize: 12, color: "#666", textTransform: "capitalize" },
  pageTitle: { fontSize: 26, fontWeight: 600, color: "#111", marginTop: 4 },
  subtitle:  { fontSize: 13, color: "#666", marginTop: 4 },
  topActions:{ display: "flex", alignItems: "center", gap: 10 },
  dateInput: {
    padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd",
    background: "#fff", fontSize: 13,
  },
  badge: {
    background: "#E6F1FB", color: "#0C447C",
    padding: "6px 12px", borderRadius: 20, fontSize: 12, fontWeight: 500,
  },
  panelCard: {
    background: "#fff", borderRadius: 12, padding: "20px 22px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.06)", marginBottom: 18,
  },
  sectionHeader: {
    display: "flex", justifyContent: "space-between", alignItems: "flex-start",
    gap: 16, marginBottom: 14,
  },
  sectionLabel: {
    fontSize: 11, fontWeight: 600, color: "#378ADD",
    textTransform: "uppercase", letterSpacing: "0.6px",
  },
  sectionTitle: { fontSize: 18, fontWeight: 600, color: "#111", marginTop: 4 },
  timeBig: {
    fontFamily: "'Space Mono', monospace",
    fontSize: 28, fontWeight: 700, color: "#185FA5",
  },
  metaRow: { display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 18 },
  chip: {
    display: "inline-block", padding: "4px 10px", borderRadius: 20,
    fontSize: 12, fontWeight: 500,
  },
  chipMuted: {
    display: "inline-block", padding: "4px 10px", borderRadius: 20,
    fontSize: 12, color: "#666", background: "#F0F0F0",
  },
  stationsTitle: {
    fontSize: 13, fontWeight: 600, color: "#333", marginBottom: 12,
  },
  stationsList: { display: "flex", flexDirection: "column", gap: 0 },
  stationItem:  { display: "flex", gap: 12, minHeight: 52 },
  stationTrack: { width: 18, display: "flex", flexDirection: "column", alignItems: "center" },
  stationDot:   { width: 10, height: 10, borderRadius: "50%", marginTop: 4, flexShrink: 0 },
  stationLine:  { width: 2, flex: 1, background: "#D6E8FA", marginTop: 2 },
  stationBody:  { paddingBottom: 12 },
  stationName:  { fontSize: 14, fontWeight: 500, color: "#111" },
  stationCode:  {
    fontFamily: "'Space Mono', monospace", fontSize: 11,
    color: "#378ADD", marginRight: 8,
  },
  stationMeta:  { fontSize: 12, color: "#777", marginTop: 2 },
  panelTitle:   { fontSize: 15, fontWeight: 600, color: "#111", marginBottom: 14 },
  tableWrap:    { overflowX: "auto" },
  table:        { width: "100%", borderCollapse: "collapse" },
  th: {
    textAlign: "left", fontSize: 11, color: "#888",
    textTransform: "uppercase", letterSpacing: "0.5px",
    padding: "8px 10px", borderBottom: "1px solid #eee",
  },
  td:       { padding: "12px 10px", borderBottom: "1px solid #f0f0f0", verticalAlign: "top" },
  tdStrong: { padding: "12px 10px", borderBottom: "1px solid #f0f0f0", fontWeight: 600, color: "#185FA5" },
  routeCode:{ fontFamily: "'Space Mono', monospace", fontSize: 12, color: "#378ADD" },
  routeName:{ fontSize: 13, color: "#333", marginTop: 2 },
  rowHighlight:{ background: "#F7FBFF" },
  empty:    { padding: 32, textAlign: "center", color: "#888", fontSize: 14 },
  errorBox: {
    background: "#FCEBEB", border: "1px solid #F7C1C1",
    color: "#791F1F", borderRadius: 8, padding: "12px 14px", marginBottom: 16,
    fontSize: 13,
  },
};
