import { useState } from "react";
import Sidebar from "../components/Sidebar";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Reportes({ user, onNav, onLogout }) {
  const [loading, setLoading] = useState(null); // "pdf" | "xlsx" | null
  const [feedback, setFeedback] = useState(null); // { ok, msg }
  const hoy = new Date().toISOString().slice(0, 10);
  const haceUnaSemana = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const [fecha, setFecha] = useState(hoy);

  const handleExport = async (formato) => {
    setLoading(formato);
    setFeedback(null);
    try {
      const token = localStorage.getItem("metrohub_access_token");
      const res = await fetch(`${BASE}/api/reportes/exportar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ formato, usar_familia_atu: true, fecha }),
      });

      if (!res.ok) {
        let msg = `${res.status} ${res.statusText}`;
        try { const e = await res.json(); if (e.detail) msg = e.detail; } catch {}
        throw new Error(msg);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `metrohub_reporte_atu.${formato}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setFeedback({ ok: true, msg: `Reporte ${formato.toUpperCase()} descargado correctamente.` });
    } catch (e) {
      setFeedback({ ok: false, msg: e.message || "No se pudo generar el reporte." });
    } finally {
      setLoading(null);
      setTimeout(() => setFeedback(null), 4000);
    }
  };

  const esAdmin = user?.role === "admin_atu";

  return (
    <div style={styles.layout}>
      <Sidebar active="reportes" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Exportación</div>
            <h1 style={styles.pageTitle}>Reportes ATU</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {!esAdmin && (
          <div style={styles.infoBox}>
            Solo el Administrador ATU puede generar y exportar reportes.
          </div>
        )}

        {esAdmin && (
          <div style={styles.dateRow}>
            <label style={styles.dateLabel}>Fecha del reporte</label>
            <input
              type="date"
              value={fecha}
              min={haceUnaSemana}
              max={hoy}
              onChange={e => setFecha(e.target.value)}
              style={styles.dateInput}
            />
          </div>
        )}

        {esAdmin && (
          <div style={styles.cardsRow}>
            <ExportCard
              titulo="Reporte PDF"
              desc="KPIs operativos del sistema en formato PDF con tabla formateada."
              ext="PDF"
              color="#042C53"
              loading={loading === "pdf"}
              onExport={() => handleExport("pdf")}
            />
            <ExportCard
              titulo="Reporte XLSX"
              desc="KPIs operativos del sistema en hoja de cálculo Excel con formato de tabla."
              ext="XLSX"
              color="#185FA5"
              loading={loading === "xlsx"}
              onExport={() => handleExport("xlsx")}
            />
          </div>
        )}

        {feedback && (
          <div style={feedback.ok ? styles.feedbackOk : styles.feedbackErr}>
            {feedback.msg}
          </div>
        )}

        <div style={styles.noteBox}>
          <strong>¿Qué incluye el reporte?</strong>
          <ul style={styles.noteList}>
            <li>Rutas activas</li>
            <li>Choferes activos y buses operativos</li>
            <li>Asignaciones confirmadas del día</li>
            <li>Conflictos abiertos pendientes de resolución</li>
            <li>Certificaciones por vencer en los próximos 30 días</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

function ExportCard({ titulo, desc, ext, color, loading, onExport }) {
  return (
    <div style={styles.card}>
      <div style={{ ...styles.cardBadge, background: color }}>{ext}</div>
      <div style={styles.cardTitle}>{titulo}</div>
      <div style={styles.cardDesc}>{desc}</div>
      <button
        style={{ ...styles.exportBtn, background: color, opacity: loading ? 0.6 : 1 }}
        onClick={onExport}
        disabled={loading}
      >
        {loading ? "Generando…" : `Descargar ${ext}`}
      </button>
    </div>
  );
}

const styles = {
  layout:     { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main:       { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 20, overflow: "auto" },
  topbar:     { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  breadcrumb: { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3 },
  pageTitle:  { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge:      { background: "#185FA5", color: "#E6F1FB", fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, padding: "5px 12px", borderRadius: 20 },
  infoBox:    { background: "#FAEEDA", border: "1px solid #F0D1A0", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#633806" },
  cardsRow:   { display: "flex", gap: 16, flexWrap: "wrap" },
  card:       { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, padding: "24px 22px", display: "flex", flexDirection: "column", gap: 10, minWidth: 240, flex: 1 },
  cardBadge:  { display: "inline-block", color: "#fff", fontFamily: "'Space Mono',monospace", fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 4, width: "fit-content" },
  cardTitle:  { fontFamily: "'DM Sans',sans-serif", fontSize: 16, fontWeight: 600, color: "#111" },
  cardDesc:   { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#666", lineHeight: 1.5, flex: 1 },
  exportBtn:  { color: "#E6F1FB", border: "none", borderRadius: 8, padding: "10px 18px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, cursor: "pointer", marginTop: 8 },
  feedbackOk: { background: "#EAF3DE", border: "1px solid #C0DD97", borderRadius: 8, padding: "11px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#27500A" },
  feedbackErr:{ background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 8, padding: "11px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  noteBox:    { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 8, padding: "16px 20px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444" },
  noteList:   { marginTop: 8, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "#666" },
  dateRow:    { display: "flex", alignItems: "center", gap: 10 },
  dateLabel:  { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#555", fontWeight: 500 },
  dateInput:  { fontSize: 13, padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#111", outline: "none", fontFamily: "'DM Sans',sans-serif" },
};
