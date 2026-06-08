import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TIPO_COLOR = {
  regular:  { bg: "#E6F1FB", color: "#0C447C" },
  expreso:  { bg: "#EAF3DE", color: "#27500A" },
  nocturna: { bg: "#F3E6FB", color: "#4A0C7C" },
};

const FORM_INIT = {
  codigo: "", nombre: "", tipo: "regular",
  hora_inicio: "05:00", hora_fin: "23:00", frecuencia_min: 10,
};

export default function Rutas({ user, onNav, onLogout }) {
  const [rutas, setRutas]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [modal, setModal]       = useState(false);
  const [form, setForm]         = useState(FORM_INIT);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError]   = useState("");

  useEffect(() => {
    api.get("/api/rutas")
      .then(data => { setRutas(data); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, []);

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleCrear = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.codigo.trim() || !form.nombre.trim()) {
      setFormError("Código y nombre son obligatorios.");
      return;
    }
    setSubmitting(true);
    try {
      const nueva = await api.post("/api/rutas", {
        ...form,
        frecuencia_min: Number(form.frecuencia_min),
      });
      setRutas(prev => [...prev, nueva]);
      setModal(false);
      setForm(FORM_INIT);
    } catch (e) {
      setFormError(e.message || "No se pudo crear la ruta.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="rutas" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Catálogo operativo</div>
            <h1 style={styles.pageTitle}>Rutas y Estaciones</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {user?.role === "admin_atu" && (
              <button style={styles.btnPrimary} onClick={() => setModal(true)}>
                + Nueva ruta
              </button>
            )}
            <div style={styles.badge}>
              {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
            </div>
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
                      <td style={styles.td}>{r.hora_inicio} – {r.hora_fin}</td>
                      <td style={styles.td}>Cada {r.frecuencia_min} min</td>
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

      {/* Modal nueva ruta */}
      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nueva ruta</h2>
            <form onSubmit={handleCrear} style={styles.form}>
              <ModalField label="Código">
                <input name="codigo" value={form.codigo} onChange={handleField}
                  placeholder="ej. SIT-1" style={styles.input} maxLength={20} />
              </ModalField>
              <ModalField label="Nombre">
                <input name="nombre" value={form.nombre} onChange={handleField}
                  placeholder="ej. Naranjal - Matellini" style={styles.input} />
              </ModalField>
              <ModalField label="Tipo">
                <select name="tipo" value={form.tipo} onChange={handleField} style={styles.input}>
                  <option value="regular">Regular</option>
                  <option value="expreso">Expreso</option>
                  <option value="nocturna">Nocturna</option>
                </select>
              </ModalField>
              <div style={{ display: "flex", gap: 12 }}>
                <ModalField label="Hora inicio" style={{ flex: 1 }}>
                  <input type="time" name="hora_inicio" value={form.hora_inicio}
                    onChange={handleField} style={styles.input} />
                </ModalField>
                <ModalField label="Hora fin" style={{ flex: 1 }}>
                  <input type="time" name="hora_fin" value={form.hora_fin}
                    onChange={handleField} style={styles.input} />
                </ModalField>
              </div>
              <ModalField label="Frecuencia (min)">
                <input type="number" name="frecuencia_min" value={form.frecuencia_min}
                  onChange={handleField} min={2} max={60} style={styles.input} />
              </ModalField>

              {formError && <div style={styles.formErr}>{formError}</div>}

              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModal(false); setFormError(""); setForm(FORM_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submitting}>
                  {submitting ? "Creando…" : "Crear ruta"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function ModalField({ label, children, style }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, ...style }}>
      <label style={{ fontSize: 11, fontWeight: 500, color: "#666",
        textTransform: "uppercase", letterSpacing: "0.5px" }}>{label}</label>
      {children}
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
  btnPrimary:{ padding: "8px 18px", borderRadius: 8, border: "none", background: "#185FA5",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer" },
  btnSecondary:{ padding: "8px 16px", borderRadius: 8, border: "1px solid #ddd", background: "#fff",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444", cursor: "pointer" },
  tableWrap: { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:     { width: "100%", borderCollapse: "collapse" },
  th:        { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:        { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:       { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  footer:    { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:     { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:  { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:   { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:     { background: "#fff", borderRadius: 12, padding: 28, width: 420, maxWidth: "95vw", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle:{ fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:      { display: "flex", flexDirection: "column", gap: 14 },
  input:     { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd",
    background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:   { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
