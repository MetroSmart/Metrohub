import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import KpiCard from "../components/KpiCard";
import RouteBar from "../components/RouteBar";
import AlertPanel from "../components/AlertPanel";
import { api } from "../api";

export default function Dashboard({ user, onNav, onLogout }) {
  const [kpis, setKpis]     = useState(null);
  const [rutas, setRutas]   = useState([]);
  const [alertas, setAlertas] = useState([]);

  const now = new Date().toLocaleDateString("es-PE", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  useEffect(() => {
    api.get("/api/dashboard").then(setKpis).catch(() => {});
    api.get("/api/rutas?solo_activas=true").then(setRutas).catch(() => {});
    api.get("/api/choferes/alertas/documentos")
      .then(d => setAlertas(d.choferes ?? []))
      .catch(() => {});
  }, []);

  const kpiCards = kpis ? [
    { label: "Rutas activas",        value: String(kpis.rutas_activas),          sub: "en operación hoy",       tone: "good"   },
    { label: "Choferes activos",     value: String(kpis.choferes_activos),       sub: `${kpis.buses_operativos} buses operativos`, tone: "good" },
    { label: "Conflictos abiertos",  value: String(kpis.conflictos_abiertos),    sub: "pendientes de resolver", tone: kpis.conflictos_abiertos > 0 ? "danger" : "good" },
    { label: "Certif. por vencer",   value: String(kpis.certif_por_vencer_30d),  sub: "próximos 30 días",       tone: kpis.certif_por_vencer_30d > 0 ? "warn" : "good" },
  ] : [];

  const alertItems = alertas.slice(0, 5).map(c => ({
    type: c.estado === "VENCIDA" ? "danger" : "warn",
    text: `${c.estado === "VENCIDA" ? "Certif. VENCIDA" : "Certif. por vencer"} — ${c.nombres} ${c.apellidos} (${c.dias_certif}d)`,
    time: `vence ${c.fec_vence_certif_prot}`,
  }));

  return (
    <div style={styles.layout}>
      <Sidebar active="dashboard" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.dateStr}>{now}</div>
            <h1 style={styles.pageTitle}>Dashboard operativo</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* KPIs */}
        <div style={styles.kpiGrid}>
          {kpis
            ? kpiCards.map(k => <KpiCard key={k.label} {...k} />)
            : [1,2,3,4].map(i => <div key={i} style={styles.kpiSkeleton} />)
          }
        </div>

        {/* Rutas + Alertas */}
        <div style={styles.row}>
          <div style={{ flex: 1.4 }}>
            <div style={styles.panelCard}>
              <div style={styles.panelTitle}>Rutas activas</div>
              {rutas.length === 0
                ? <div style={styles.empty}>Cargando rutas…</div>
                : rutas.map(r => (
                    <RouteBar key={r.id} code={r.codigo} name={r.nombre} pct={100} />
                  ))
              }
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <AlertPanel alerts={alertItems.length ? alertItems : [{ type: "info", text: "Sin alertas de documentos", time: "ahora" }]} />
          </div>
        </div>

        {/* Acceso rápido */}
        <div style={styles.quickRow}>
          <button style={styles.quickBtn} onClick={() => onNav("grilla")}>
            Ver grilla de horarios →
          </button>
          <button style={styles.quickBtn} onClick={() => onNav("choferes")}>
            Ver choferes →
          </button>
          <button style={styles.quickBtn} onClick={() => onNav("rutas")}>
            Ver rutas →
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