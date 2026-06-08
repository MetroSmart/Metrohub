import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const FORM_INIT = {
  ruc: "", razon_social: "", nombre_corto: "",
  telefono: "", email_contacto: "",
};

export default function Concesionarios({ user, onNav, onLogout }) {
  const [concesionarios, setConcs] = useState([]);
  const [loading, setLoading]      = useState(true);
  const [error, setError]          = useState(null);
  const [modal, setModal]          = useState(false);
  const [form, setForm]            = useState(FORM_INIT);
  const [submitting, setSubmitting]= useState(false);
  const [formError, setFormError]  = useState("");

  useEffect(() => {
    api.get("/api/concesionarios")
      .then(d => { setConcs(d.concesionarios ?? []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleCrear = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.ruc.trim() || !form.razon_social.trim() || !form.nombre_corto.trim()) {
      setFormError("RUC, razón social y nombre corto son obligatorios.");
      return;
    }
    if (form.ruc.length !== 11 || !/^\d+$/.test(form.ruc)) {
      setFormError("El RUC debe tener exactamente 11 dígitos.");
      return;
    }
    setSubmitting(true);
    try {
      const nuevo = await api.post("/api/concesionarios", {
        ruc:            form.ruc.trim(),
        razon_social:   form.razon_social.trim(),
        nombre_corto:   form.nombre_corto.trim(),
        telefono:       form.telefono.trim() || null,
        email_contacto: form.email_contacto.trim() || null,
      });
      setConcs(prev => [...prev, nuevo]);
      setModal(false);
      setForm(FORM_INIT);
    } catch (e) {
      setFormError(e.message || "No se pudo crear el concesionario.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActivo = async (id, activo) => {
    try {
      const actualizado = await api.patch(`/api/concesionarios/${id}`, { activo: !activo });
      setConcs(prev => prev.map(c => c.id === id ? { ...c, activo: actualizado.activo } : c));
    } catch (e) {
      alert(e.message || "No se pudo actualizar.");
    }
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="concesionarios" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Administración</div>
            <h1 style={styles.pageTitle}>Concesionarios</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button style={styles.btnPrimary} onClick={() => setModal(true)}>
              + Nuevo concesionario
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
                  {["RUC","Razón social","Nombre corto","Teléfono","Email","Estado",""].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {concesionarios.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                      Sin concesionarios registrados.
                    </td>
                  </tr>
                )}
                {concesionarios.map(c => (
                  <tr key={c.id}>
                    <td style={styles.td}>
                      <span style={{ fontFamily: "'Space Mono',monospace", fontSize: 12 }}>{c.ruc}</span>
                    </td>
                    <td style={styles.td}>{c.razon_social}</td>
                    <td style={styles.td}><strong>{c.nombre_corto}</strong></td>
                    <td style={styles.td}>{c.telefono ?? "—"}</td>
                    <td style={styles.td}>{c.email_contacto ?? "—"}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.tag,
                        background: c.activo ? "#EAF3DE" : "#f0f0f0",
                        color:      c.activo ? "#27500A" : "#888",
                      }}>
                        {c.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <button
                        onClick={() => handleToggleActivo(c.id, c.activo)}
                        style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}
                      >
                        {c.activo ? "Desactivar" : "Activar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={styles.footer}>{concesionarios.length} concesionarios</div>
          </div>
        )}
      </main>

      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nuevo concesionario</h2>
            <form onSubmit={handleCrear} style={styles.form}>
              <Field label="RUC (11 dígitos) *">
                <input name="ruc" value={form.ruc} onChange={handleField}
                  placeholder="20123456789" maxLength={11} style={styles.input} />
              </Field>
              <Field label="Razón social *">
                <input name="razon_social" value={form.razon_social} onChange={handleField}
                  placeholder="Ej. Transportes Lima S.A.C." style={styles.input} />
              </Field>
              <Field label="Nombre corto *">
                <input name="nombre_corto" value={form.nombre_corto} onChange={handleField}
                  placeholder="Ej. TransLima" style={styles.input} maxLength={50} />
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Teléfono" style={{ flex: 1 }}>
                  <input name="telefono" value={form.telefono} onChange={handleField}
                    placeholder="Ej. 01-234-5678" style={styles.input} />
                </Field>
                <Field label="Email contacto" style={{ flex: 1 }}>
                  <input type="email" name="email_contacto" value={form.email_contacto}
                    onChange={handleField} placeholder="contacto@empresa.com" style={styles.input} />
                </Field>
              </div>

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
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 460, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
