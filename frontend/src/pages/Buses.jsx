import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const ESTADO_STYLE = {
  operativo:    { bg: "#EAF3DE", color: "#27500A" },
  mantenimiento:{ bg: "#FAEEDA", color: "#633806" },
  reparacion:   { bg: "#FFF8E1", color: "#7A5800" },
  baja:         { bg: "#f0f0f0", color: "#888"    },
};
const TIPO_STYLE = {
  articulado:   { bg: "#E6F1FB", color: "#0C447C" },
  convencional: { bg: "#F3E6FB", color: "#4A0C7C" },
};

const FORM_INIT = {
  placa: "", concesionario_id: "", tipo: "articulado",
  anio: "", capacidad_pasajeros: "", estado: "operativo",
};

export default function Buses({ user, onNav, onLogout }) {
  const [buses, setBuses]               = useState([]);
  const [concesionarios, setConces]     = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [modal, setModal]               = useState(false);
  const [form, setForm]                 = useState(FORM_INIT);
  const [submitting, setSubmitting]     = useState(false);
  const [formError, setFormError]       = useState("");

  const isAdmin = user?.role === "admin_atu";

  useEffect(() => {
    api.get("/api/concesionarios?solo_activos=true")
      .then(d => setConces(d.concesionarios ?? []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filtroEstado) params.set("estado", filtroEstado);
    api.get(`/api/buses?${params}`)
      .then(d => { setBuses(d.buses ?? []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [filtroEstado]);

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleCrear = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.placa.trim() || !form.concesionario_id) {
      setFormError("Placa y concesionario son obligatorios.");
      return;
    }
    setSubmitting(true);
    try {
      const nuevo = await api.post("/api/buses", {
        placa:               form.placa.trim().toUpperCase(),
        concesionario_id:    Number(form.concesionario_id),
        tipo:                form.tipo,
        anio:                form.anio ? Number(form.anio) : null,
        capacidad_pasajeros: form.capacidad_pasajeros ? Number(form.capacidad_pasajeros) : null,
        estado:              form.estado,
      });
      setBuses(prev => [...prev, nuevo]);
      setModal(false);
      setForm(FORM_INIT);
    } catch (e) {
      setFormError(e.message || "No se pudo registrar el bus.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEstado = async (placa, nuevoEstado) => {
    try {
      const actualizado = await api.patch(`/api/buses/${placa}`, { estado: nuevoEstado });
      setBuses(prev => prev.map(b => b.placa === placa ? { ...b, estado: actualizado.estado } : b));
    } catch (e) {
      alert(e.message || "No se pudo cambiar el estado.");
    }
  };

  const handleEliminar = async (placa) => {
    if (!window.confirm(`¿Eliminar el bus ${placa}? Esta acción no se puede deshacer.`)) return;
    try {
      await api.delete(`/api/buses/${placa}`);
      setBuses(prev => prev.filter(b => b.placa !== placa));
    } catch (e) {
      alert(e.message || "No se pudo eliminar el bus.");
    }
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="buses" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Operaciones</div>
            <h1 style={styles.pageTitle}>Flota de buses</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {isAdmin && (
              <button style={styles.btnPrimary} onClick={() => setModal(true)}>
                + Registrar bus
              </button>
            )}
            <div style={styles.badge}>{isAdmin ? "Admin ATU" : "Supervisor"}</div>
          </div>
        </div>

        <div>
          <select value={filtroEstado} onChange={e => setFiltroEstado(e.target.value)} style={styles.select}>
            <option value="">Todos los estados</option>
            <option value="operativo">Operativo</option>
            <option value="mantenimiento">Mantenimiento</option>
            <option value="reparacion">Reparación</option>
            <option value="baja">Baja</option>
          </select>
        </div>

        {loading && <div style={styles.empty}>Cargando buses…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {!loading && !error && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Placa","Tipo","Año","Capacidad","Concesionario","Estado",""].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {buses.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                      Sin buses registrados.
                    </td>
                  </tr>
                )}
                {buses.map(b => {
                  const est = ESTADO_STYLE[b.estado] ?? ESTADO_STYLE.baja;
                  const tip = TIPO_STYLE[b.tipo]   ?? {};
                  const conc = concesionarios.find(c => c.id === b.concesionario_id);
                  return (
                    <tr key={b.placa}>
                      <td style={styles.td}>
                        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: 12, fontWeight: 600 }}>
                          {b.placa}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: tip.bg ?? "#f0f0f0", color: tip.color ?? "#444" }}>
                          {b.tipo}
                        </span>
                      </td>
                      <td style={styles.td}>{b.anio ?? "—"}</td>
                      <td style={styles.td}>{b.capacidad_pasajeros ? `${b.capacidad_pasajeros} pax` : "—"}</td>
                      <td style={styles.td}>{conc ? conc.nombre_corto : `#${b.concesionario_id}`}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: est.bg, color: est.color }}>
                          {b.estado}
                        </span>
                      </td>
                      <td style={styles.td}>
                        {isAdmin && (
                          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                            <select
                              value={b.estado}
                              onChange={e => handleEstado(b.placa, e.target.value)}
                              style={{ ...styles.select, fontSize: 11, padding: "4px 8px" }}
                            >
                              <option value="operativo">Operativo</option>
                              <option value="mantenimiento">Mantenimiento</option>
                              <option value="reparacion">Reparación</option>
                              <option value="baja">Baja</option>
                            </select>
                            <button
                              onClick={() => handleEliminar(b.placa)}
                              style={styles.btnDelete}
                              title="Eliminar bus"
                            >
                              Eliminar
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{buses.length} buses en total</div>
          </div>
        )}
      </main>

      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Registrar bus</h2>
            <form onSubmit={handleCrear} style={styles.form}>
              <Field label="Placa *">
                <input name="placa" value={form.placa} onChange={handleField}
                  placeholder="Ej. ABC-123" style={styles.input} maxLength={10} />
              </Field>
              <Field label="Concesionario *">
                <select name="concesionario_id" value={form.concesionario_id}
                  onChange={handleField} style={styles.input}>
                  <option value="">— Seleccionar —</option>
                  {concesionarios.map(c => (
                    <option key={c.id} value={c.id}>{c.nombre_corto} — {c.ruc}</option>
                  ))}
                </select>
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Tipo *" style={{ flex: 1 }}>
                  <select name="tipo" value={form.tipo} onChange={handleField} style={styles.input}>
                    <option value="articulado">Articulado</option>
                    <option value="convencional">Convencional</option>
                  </select>
                </Field>
                <Field label="Estado" style={{ flex: 1 }}>
                  <select name="estado" value={form.estado} onChange={handleField} style={styles.input}>
                    <option value="operativo">Operativo</option>
                    <option value="mantenimiento">Mantenimiento</option>
                    <option value="reparacion">Reparación</option>
                    <option value="baja">Baja</option>
                  </select>
                </Field>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Año de fabricación" style={{ flex: 1 }}>
                  <input type="number" name="anio" value={form.anio}
                    onChange={handleField} placeholder="Ej. 2019" min={1990} max={2100}
                    style={styles.input} />
                </Field>
                <Field label="Capacidad (pasajeros)" style={{ flex: 1 }}>
                  <input type="number" name="capacidad_pasajeros"
                    value={form.capacidad_pasajeros} onChange={handleField}
                    placeholder="Ej. 160" min={1} style={styles.input} />
                </Field>
              </div>

              {formError && <div style={styles.formErr}>{formError}</div>}

              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModal(false); setFormError(""); setForm(FORM_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submitting}>
                  {submitting ? "Registrando…" : "Registrar"}
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
  footer:     { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:      { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:   { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 460, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
  btnDelete:  { padding: "4px 10px", borderRadius: 6, border: "1px solid #F7C1C1", background: "#FCEBEB", color: "#791F1F", fontSize: 11, cursor: "pointer", fontFamily: "'DM Sans',sans-serif" },
};
