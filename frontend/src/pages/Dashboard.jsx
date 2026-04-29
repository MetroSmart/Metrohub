import Sidebar from "../components/Sidebar";
import KpiCard from "../components/KpiCard";
import RouteBar from "../components/RouteBar";
import AlertPanel from "../components/AlertPanel";

const KPI_DATA = [
  { label: "Rutas activas",        value: "18",  sub: "de 20 programadas",  tone: "good"   },
  { label: "Choferes asignados",   value: "142", sub: "94% disponibles",    tone: "good"   },
  { label: "Conflictos",           value: "3",   sub: "pendientes hoy",     tone: "danger" },
  { label: "Licencias por vencer", value: "7",   sub: "próximos 30 días",   tone: "warn"   },
];

const ROUTES = [
  { code: "RT-A", name: "Naranjal → Matellini",   pct: 96 },
  { code: "RT-B", name: "Naranjal → Chorrillos",  pct: 88 },
  { code: "EXP",  name: "Expreso 1",               pct: 72 },
  { code: "RT-C", name: "Comas → Barranco",        pct: 61 },
  { code: "EX2",  name: "Expreso 2",               pct: 100 },
];

const ALERTS = [
  { type: "danger", text: "Conflicto de turno — Chofer #C-047 (RT-C, 08:00h)", time: "hace 12 min" },
  { type: "danger", text: "Unidad #U-112 sin asignar — Expreso 1",             time: "hace 34 min" },
  { type: "warn",   text: "Licencia vence en 5 días — Chofer #C-028",          time: "hoy"         },
  { type: "info",   text: "Propuesta IA lista para revisión — semana 18",      time: "hace 1 h"    },
];

export default function Dashboard({ user, onNav, onLogout }) {
  const now = new Date().toLocaleDateString("es-PE", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  return (
    <div style={styles.layout}>
      <Sidebar active="dashboard" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        {/* Topbar */}
        <div style={styles.topbar}>
          <div>
            <div style={styles.dateStr}>{now}</div>
            <h1 style={styles.pageTitle}>Dashboard operativo</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* KPIs */}
        <div style={styles.kpiGrid}>
          {KPI_DATA.map(k => (
            <KpiCard key={k.label} {...k} />
          ))}
        </div>

        {/* Rutas + Alertas */}
        <div style={styles.row}>
          <div style={{ flex: 1.4 }}>
            <div style={styles.panelCard}>
              <div style={styles.panelTitle}>Cobertura por ruta</div>
              {ROUTES.map(r => <RouteBar key={r.code} {...r} />)}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <AlertPanel alerts={ALERTS} />
          </div>
        </div>

        {/* Acceso rápido */}
        <div style={styles.quickRow}>
          <button style={styles.quickBtn} onClick={() => onNav("grilla")}>
            Ver grilla de horarios →
          </button>
          <button style={{ ...styles.quickBtn, background: "#EAF3DE", color: "#27500A", borderColor: "#C0DD97" }}>
            Solicitar propuesta IA →
          </button>
          <button style={{ ...styles.quickBtn, background: "#E6F1FB", color: "#0C447C", borderColor: "#B5D4F4" }}>
            Exportar reporte PDF →
          </button>
        </div>
      </main>
    </div>
  );
}

const styles = {
  layout: { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main: { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 20, overflow: "auto" },
  topbar: { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  dateStr: { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3, textTransform: "capitalize" },
  pageTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge: {
    background: "#185FA5", color: "#E6F1FB",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 11, fontWeight: 500,
    padding: "5px 12px", borderRadius: 20,
  },
  kpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, minmax(0,1fr))",
    gap: 12,
  },
  row: { display: "flex", gap: 14 },
  panelCard: {
    background: "#fff",
    border: "0.5px solid #e8e8e8",
    borderRadius: 8,
    padding: 14,
  },
  panelTitle: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, fontWeight: 500, color: "#111", marginBottom: 10,
  },
  quickRow: { display: "flex", gap: 10, flexWrap: "wrap" },
  quickBtn: {
    padding: "10px 18px",
    borderRadius: 8,
    border: "1px solid #ddd",
    background: "#fff",
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 13, color: "#444",
    cursor: "pointer",
  },
};