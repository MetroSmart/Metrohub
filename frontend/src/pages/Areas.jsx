import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const FORM_INIT = { nombre: "", nombre_corto: "", descripcion: "" };

export default function Areas({ user, onNav, onLogout }) {
  const [areas, setAreas]          = useState([]);
  const [loading, setLoading]      = useState(true);
  const [error, setError]          = useState(null);
  const [modal, setModal]          = useState(false);
  const [form, setForm]            = useState(FORM_INIT);
  const [submitting, setSubmitting]= useState(false);
  const [formError, setFormError]  = useState("");

  useEffect(() => {
    api.get("/api/areas")
      .then(d => { setAreas(d.areas ?? []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleCrear = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.nombre.trim() || !form.nombre_corto.trim()) {
      setFormError("Nombre y nombre corto son obligatorios.");
      return;
    }
    setSubmitting(true);
    try {
      const nueva = await api.post("/api/areas", {
        nombre:       form.nombre.trim(),
        nombre_corto: form.nombre_corto.trim(),
        descripcion:  form.descripcion.trim() || null,
      });
      setAreas(prev => [...prev, nueva]);
      setModal(false);
      setForm(FORM_INIT);
    } catch (e) {
      setFormError(e.message || "No se pudo crear el área.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActivo = async (id, activo) => {
    try {
      const actualizado = await api.patch(`/api/areas/${id}`, { activo: !activo });
      setAreas(prev => prev.map(a => a.id === id ? { ...a, activo: actualizado.activo } : a));
    } catch (e) {
      alert(e.message || "No se pudo actualizar.");
    }
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="areas" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Administración</div>
            <h1 style={styles.pageTitle}>Áreas Operativas</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button style={styles.btnPrimary} onClick={() => setModal(true)}>
              + Nueva área
            </button>
            <div style={styles.badge}>Admin ATU</div>
          </div>
        </div>

        {loading && <div style={styles.empty}>Cargando…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {!loading && !error && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Nombre","Nombre corto","Descripción","Estado",""].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {areas.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                      Sin áreas operativas registradas.
                    </td>
                  </tr>
                )}
                {areas.map(a => (
                  <tr key={a.id}>
                    <td style={styles.td}><strong>{a.nombre}</strong></td>
                    <td style={styles.td}>
                      <span style={{ fontFamily: "'Space Mono',monospace", fontSize: 12 }}>{a.nombre_corto}</span>
                    </td>
                    <td style={styles.td}>{a.descripcion ?? "—"}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.tag,
                        background: a.activo ? "#EAF3DE" : "#f0f0f0",
                        color:      a.activo ? "#27500A" : "#888",
                      }}>
                        {a.activo ? "Activa" : "Inactiva"}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <button
                        onClick={() => handleToggleActivo(a.id, a.activo)}
                        style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}
                      >
                        {a.activo ? "Desactivar" : "Activar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={styles.footer}>{areas.length} áreas operativas</div>
          </div>
        )}
      </main>

      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nueva área operativa</h2>
            <form onSubmit={handleCrear} style={styles.form}>
              <Field label="Nombre *">
                <input name="nombre" value={form.nombre} onChange={handleField}
                  placeholder="Ej. Operaciones Norte" style={styles.input} />
              </Field>
              <Field label="Nombre corto *">
                <input name="nombre_corto" value={form.nombre_corto} onChange={handleField}
                  placeholder="Ej. Op. Norte" style={styles.input} maxLength={50} />
              </Field>
              <Field label="Descripción">
                <textarea name="descripcion" value={form.descripcion} onChange={handleField}
                  placeholder="Descripción del área y sus responsabilidades"
                  style={{ ...styles.input, resize: "vertical", minHeight: 72 }} />
              </Field>

              {formError && <div style={styles.formErr}>{formError}</div>}

              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModal(false); setFormError(""); setForm(FORM_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submitting}>
                  {submitting ? "Creando…" : "Crear"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children, style }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, ...style }}>
      <label style={{ fontSize: 11, fontWeight: 500, color: "#666",
        textTransform: "uppercase", letterSpacing: "0.5px" }}>{label}</label>
      {children}
    </div>
  );
}

const styles = {
  layout:     { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main:       { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 18, overflow: "auto" },
  topbar:     { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  breadcrumb: { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3 },
  pageTitle:  { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge:      { background: "#185FA5", color: "#E6F1FB", fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, padding: "5px 12px", borderRadius: 20 },
  btnPrimary: { padding: "8px 18px", borderRadius: 8, border: "none", background: "#185FA5", fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer" },
  btnSecondary:{ padding: "8px 16px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444", cursor: "pointer" },
  tableWrap:  { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:      { width: "100%", borderCollapse: "collapse" },
  th:         { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:         { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:        { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  footer:     { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:      { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:   { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 480, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
