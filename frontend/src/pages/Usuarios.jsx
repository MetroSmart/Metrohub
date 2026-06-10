import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const ROL_STYLE = {
  admin_atu:                { bg: "#E6F1FB", color: "#0C447C" },
  supervisor_area: { bg: "#EAF3DE", color: "#27500A" },
};

const FORM_INIT = {
  email: "", password: "", nombre: "", apellidos: "",
  dni: "", rol: "supervisor_area", area_id: "",
};

export default function Usuarios({ user, onNav, onLogout }) {
  const [usuarios, setUsuarios]       = useState([]);
  const [areas, setConces]   = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [filtroRol, setFiltroRol]     = useState("");
  const [modal, setModal]             = useState(false);
  const [form, setForm]               = useState(FORM_INIT);
  const [submitting, setSubmitting]   = useState(false);
  const [formError, setFormError]     = useState("");
  const [pwdModal, setPwdModal]       = useState(null); // id del usuario
  const [newPwd, setNewPwd]           = useState("");
  const [pwdErr, setPwdErr]           = useState("");
  const [pwdSaving, setPwdSaving]     = useState(false);

  useEffect(() => {
    api.get("/api/areas?solo_activos=true")
      .then(d => setConces(d.areas ?? []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filtroRol) params.set("rol", filtroRol);
    api.get(`/api/usuarios?${params}`)
      .then(d => { setUsuarios(d.usuarios ?? []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [filtroRol]);

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleCrear = async (e) => {
    e.preventDefault();
    setFormError("");
    const required = ["email", "password", "nombre", "apellidos", "dni"];
    for (const k of required) {
      if (!form[k].trim()) {
        setFormError(`El campo "${k}" es obligatorio.`);
        return;
      }
    }
    if (form.rol === "supervisor_area" && !form.area_id) {
      setFormError("El supervisor debe tener un área asignado.");
      return;
    }
    setSubmitting(true);
    try {
      const nuevo = await api.post("/api/usuarios", {
        email:            form.email.trim(),
        password:         form.password,
        nombre:           form.nombre.trim(),
        apellidos:        form.apellidos.trim(),
        dni:              form.dni.trim(),
        rol:              form.rol,
        area_id: form.area_id ? Number(form.area_id) : null,
      });
      setUsuarios(prev => [...prev, nuevo]);
      setModal(false);
      setForm(FORM_INIT);
    } catch (e) {
      setFormError(e.message || "No se pudo crear el usuario.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActivo = async (id, activo) => {
    try {
      const actualizado = await api.patch(`/api/usuarios/${id}`, { activo: !activo });
      setUsuarios(prev => prev.map(u => u.id === id ? { ...u, activo: actualizado.activo } : u));
    } catch (e) {
      alert(e.message || "No se pudo actualizar.");
    }
  };

  const handleCambiarPwd = async (e) => {
    e.preventDefault();
    setPwdErr("");
    if (!newPwd || newPwd.length < 6) {
      setPwdErr("La contraseña debe tener al menos 6 caracteres.");
      return;
    }
    setPwdSaving(true);
    try {
      await api.patch(`/api/usuarios/${pwdModal}/password`, { nueva_password: newPwd });
      setPwdModal(null);
      setNewPwd("");
    } catch (e) {
      setPwdErr(e.message || "No se pudo cambiar la contraseña.");
    } finally {
      setPwdSaving(false);
    }
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="usuarios" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Administración</div>
            <h1 style={styles.pageTitle}>Usuarios del sistema</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button style={styles.btnPrimary} onClick={() => setModal(true)}>
              + Nuevo usuario
            </button>
            <div style={styles.badge}>Admin ATU</div>
          </div>
        </div>

        <div>
          <select value={filtroRol} onChange={e => setFiltroRol(e.target.value)} style={styles.select}>
            <option value="">Todos los roles</option>
            <option value="admin_atu">Admin ATU</option>
            <option value="supervisor_area">Supervisor área</option>
          </select>
        </div>

        {loading && <div style={styles.empty}>Cargando usuarios…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {!loading && !error && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Nombre","Email","DNI","Rol","Área","Estado",""].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {usuarios.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                      Sin usuarios registrados.
                    </td>
                  </tr>
                )}
                {usuarios.map(u => {
                  const rs = ROL_STYLE[u.rol] ?? { bg: "#f0f0f0", color: "#444" };
                  const conc = areas.find(c => c.id === u.area_id);
                  return (
                    <tr key={u.id}>
                      <td style={styles.td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                          <span style={styles.avatar}>{u.nombre[0]}{u.apellidos[0]}</span>
                          <div style={{ fontWeight: 500 }}>{u.nombre} {u.apellidos}</div>
                        </div>
                      </td>
                      <td style={styles.td}>{u.email}</td>
                      <td style={styles.td}>{u.dni}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: rs.bg, color: rs.color }}>
                          {u.rol === "admin_atu" ? "Admin ATU" : "Supervisor"}
                        </span>
                      </td>
                      <td style={styles.td}>{conc ? conc.nombre_corto : (u.area_id ? `#${u.area_id}` : "—")}</td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.tag,
                          background: u.activo ? "#EAF3DE" : "#f0f0f0",
                          color:      u.activo ? "#27500A" : "#888",
                        }}>
                          {u.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <div style={{ display: "flex", gap: 6 }}>
                          <button onClick={() => handleToggleActivo(u.id, u.activo)}
                            style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}>
                            {u.activo ? "Desactivar" : "Activar"}
                          </button>
                          <button onClick={() => { setPwdModal(u.id); setNewPwd(""); setPwdErr(""); }}
                            style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}>
                            Contraseña
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{usuarios.length} usuarios</div>
          </div>
        )}
      </main>

      {/* Modal crear usuario */}
      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nuevo usuario</h2>
            <form onSubmit={handleCrear} style={styles.form}>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Nombre *" style={{ flex: 1 }}>
                  <input name="nombre" value={form.nombre} onChange={handleField}
                    placeholder="Carlos" style={styles.input} />
                </Field>
                <Field label="Apellidos *" style={{ flex: 1 }}>
                  <input name="apellidos" value={form.apellidos} onChange={handleField}
                    placeholder="Ramírez Torres" style={styles.input} />
                </Field>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Email *" style={{ flex: 2 }}>
                  <input type="email" name="email" value={form.email} onChange={handleField}
                    placeholder="usuario@metrohub.gob.pe" style={styles.input} />
                </Field>
                <Field label="DNI (8 dígitos) *" style={{ flex: 1 }}>
                  <input name="dni" value={form.dni} onChange={handleField}
                    placeholder="12345678" maxLength={8} style={styles.input} />
                </Field>
              </div>
              <Field label="Contraseña *">
                <input type="password" name="password" value={form.password} onChange={handleField}
                  placeholder="Mínimo 6 caracteres" style={styles.input} />
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Rol *" style={{ flex: 1 }}>
                  <select name="rol" value={form.rol} onChange={handleField} style={styles.input}>
                    <option value="supervisor_area">Supervisor área</option>
                    <option value="admin_atu">Admin ATU</option>
                  </select>
                </Field>
                {form.rol === "supervisor_area" && (
                  <Field label="Área *" style={{ flex: 1 }}>
                    <select name="area_id" value={form.area_id}
                      onChange={handleField} style={styles.input}>
                      <option value="">— Seleccionar —</option>
                      {areas.map(c => (
                        <option key={c.id} value={c.id}>{c.nombre_corto}</option>
                      ))}
                    </select>
                  </Field>
                )}
              </div>

              {formError && <div style={styles.formErr}>{formError}</div>}

              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModal(false); setFormError(""); setForm(FORM_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submitting}>
                  {submitting ? "Creando…" : "Crear usuario"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal cambiar contraseña */}
      {pwdModal !== null && (
        <div style={styles.overlay} onClick={() => setPwdModal(null)}>
          <div style={{ ...styles.modal, width: 360 }} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Cambiar contraseña</h2>
            <form onSubmit={handleCambiarPwd} style={styles.form}>
              <Field label="Nueva contraseña *">
                <input type="password" value={newPwd}
                  onChange={e => setNewPwd(e.target.value)}
                  placeholder="Mínimo 6 caracteres" style={styles.input} />
              </Field>
              {pwdErr && <div style={styles.formErr}>{pwdErr}</div>}
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => setPwdModal(null)}>Cancelar</button>
                <button type="submit" style={styles.btnPrimary} disabled={pwdSaving}>
                  {pwdSaving ? "Guardando…" : "Cambiar"}
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
  select:     { fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#222", outline: "none" },
  tableWrap:  { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:      { width: "100%", borderCollapse: "collapse" },
  th:         { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:         { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:        { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  avatar:     { width: 30, height: 30, borderRadius: "50%", background: "#B5D4F4", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: "#0C447C", flexShrink: 0 },
  footer:     { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:      { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:   { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 500, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
