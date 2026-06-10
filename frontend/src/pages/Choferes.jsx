import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const ESTADO_STYLE = {
  activo:          { bg: "#EAF3DE", color: "#27500A" },
  suspendido:      { bg: "#FCEBEB", color: "#791F1F" },
  licencia_medica: { bg: "#FAEEDA", color: "#633806" },
  vacaciones:      { bg: "#E6F1FB", color: "#0C447C" },
  inactivo:        { bg: "#f0f0f0", color: "#888"    },
};
const MOTIVO_STYLE = {
  descanso:     { bg: "#E6F1FB", color: "#0C447C" },
  vacaciones:   { bg: "#EAF3DE", color: "#27500A" },
  medico:       { bg: "#FCEBEB", color: "#791F1F" },
  capacitacion: { bg: "#F3E6FB", color: "#4A0C7C" },
  personal:     { bg: "#FAEEDA", color: "#633806" },
  otro:         { bg: "#f0f0f0", color: "#555"    },
};

const FORM_INIT = {
  dni: "", nombres: "", apellidos: "", email: "",
  fecha_nacimiento: "", area_id: "",
  numero_licencia: "", tipo_licencia: "A-IIIA",
  fec_vence_licencia: "", fec_vence_certif_prot: "",
};
const DISP_INIT = {
  chofer_id: "", fecha: "", hora_desde: "08:00", hora_hasta: "18:00",
  motivo: "descanso", observaciones: "",
};

export default function Choferes({ user, onNav, onLogout }) {
  const [choferes, setChoferes]     = useState([]);
  const [areas, setConces] = useState([]);
  const [disponibilidades, setDisps]= useState([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [filtroEstado, setFiltro]   = useState("");
  const [tab, setTab]               = useState("choferes");

  // Modal chofer
  const [modal, setModal]           = useState(false);
  const [form, setForm]             = useState(FORM_INIT);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError]   = useState("");

  // Modal disponibilidad
  const [modalDisp, setModalDisp]   = useState(false);
  const [formDisp, setFormDisp]     = useState(DISP_INIT);
  const [dispErr, setDispErr]       = useState("");
  const [dispSaving, setDispSaving] = useState(false);
  const [filtroChofer, setFiltroChofer] = useState("");

  const canCreate = user?.role === "admin_atu" || user?.role === "supervisor_area";

  useEffect(() => {
    api.get("/api/areas?solo_activos=true")
      .then(d => setConces(d.areas ?? []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const url = filtroEstado ? `/api/choferes?estado=${filtroEstado}` : "/api/choferes";
    setLoading(true);
    api.get(url)
      .then(data => { setChoferes(data); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, [filtroEstado]);

  useEffect(() => {
    if (tab !== "disponibilidad") return;
    const url = filtroChofer ? `/api/disponibilidad?chofer_id=${filtroChofer}` : "/api/disponibilidad";
    api.get(url)
      .then(d => setDisps(d.disponibilidades ?? []))
      .catch(() => setDisps([]));
  }, [tab, filtroChofer]);

  const hoy = new Date();
  const diasParaVencer = (fechaStr) =>
    Math.ceil((new Date(fechaStr) - hoy) / (1000 * 60 * 60 * 24));

  const handleField = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleRegistrar = async (e) => {
    e.preventDefault();
    setFormError("");
    const required = ["dni","nombres","apellidos","fecha_nacimiento","area_id",
                      "numero_licencia","fec_vence_licencia","fec_vence_certif_prot"];
    for (const k of required) {
      if (!form[k]?.toString().trim()) {
        setFormError(`El campo "${k.replaceAll("_", " ")}" es obligatorio.`);
        return;
      }
    }
    setSubmitting(true);
    try {
      const email = form.email.trim();
      const nuevo = await api.post("/api/choferes", {
        ...form,
        email: email || null,
        area_id: Number(form.area_id),
      });
      setChoferes(prev => [...prev, nuevo]);
      setModal(false);
      setForm(FORM_INIT);
      if (nuevo.acceso_portal?.email) {
        alert(
          `Chofer registrado.\n\nAcceso al portal:\nCorreo: ${nuevo.acceso_portal.email}\nContraseña inicial: DNI (${form.dni})\n\nDeberá cambiarla en su primer ingreso.`
        );
      }
    } catch (e) {
      setFormError(e.message || "No se pudo registrar el chofer.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegistrarDisp = async (e) => {
    e.preventDefault();
    setDispErr("");
    if (!formDisp.chofer_id || !formDisp.fecha || !formDisp.hora_desde || !formDisp.hora_hasta) {
      setDispErr("Chofer, fecha, hora desde y hora hasta son obligatorios.");
      return;
    }
    setDispSaving(true);
    try {
      const nueva = await api.post("/api/disponibilidad", {
        chofer_id:     Number(formDisp.chofer_id),
        fecha:         formDisp.fecha,
        hora_desde:    formDisp.hora_desde,
        hora_hasta:    formDisp.hora_hasta,
        motivo:        formDisp.motivo,
        observaciones: formDisp.observaciones.trim() || null,
      });
      setDisps(prev => [nueva, ...prev]);
      setModalDisp(false);
      setFormDisp(DISP_INIT);
    } catch (e) {
      setDispErr(e.message || "No se pudo registrar la indisponibilidad.");
    } finally {
      setDispSaving(false);
    }
  };

  const handleEliminarDisp = async (id) => {
    try {
      await api.delete(`/api/disponibilidad/${id}`);
      setDisps(prev => prev.filter(d => d.id !== id));
    } catch (e) {
      alert(e.message || "No se pudo eliminar.");
    }
  };

  const choferNombre = (id) => {
    const c = choferes.find(c => c.id === Number(id));
    return c ? `${c.nombres} ${c.apellidos}` : `#${id}`;
  };

  return (
    <div style={styles.layout}>
      <Sidebar active="choferes" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Personal</div>
            <h1 style={styles.pageTitle}>Choferes</h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {canCreate && tab === "choferes" && (
              <button style={styles.btnPrimary} onClick={() => setModal(true)}>+ Registrar chofer</button>
            )}
            {canCreate && tab === "disponibilidad" && (
              <button style={styles.btnPrimary} onClick={() => setModalDisp(true)}>+ Registrar indisponibilidad</button>
            )}
            <div style={styles.badge}>{user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={styles.tabs}>
          {[["choferes","Choferes"],["disponibilidad","Indisponibilidades"]].map(([k,l]) => (
            <button key={k} onClick={() => setTab(k)}
              style={{ ...styles.tab, ...(tab === k ? styles.tabActive : {}) }}>
              {l}
            </button>
          ))}
        </div>

        {/* ─── Tab Choferes ─── */}
        {tab === "choferes" && (
          <>
            <div>
              <select value={filtroEstado} onChange={e => setFiltro(e.target.value)} style={styles.select}>
                <option value="">Todos los estados</option>
                {Object.keys(ESTADO_STYLE).map(e => (
                  <option key={e} value={e}>{e.replaceAll("_", " ")}</option>
                ))}
              </select>
            </div>
            {loading && <div style={styles.empty}>Cargando choferes…</div>}
            {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}
            {!loading && !error && (
              <div style={styles.tableWrap}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      {["Chofer","DNI","Licencia","Tipo","Vence licencia","Vence certif.","Estado"].map(h => (
                        <th key={h} style={styles.th}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {choferes.map(c => {
                      const est = ESTADO_STYLE[c.estado] ?? ESTADO_STYLE.inactivo;
                      const diasLic  = diasParaVencer(c.fec_vence_licencia);
                      const diasCert = diasParaVencer(c.fec_vence_certif_prot);
                      const licA  = diasLic  <= 30;
                      const certA = diasCert <= 30;
                      return (
                        <tr key={c.id} style={{ background: (licA || certA) ? "#fffdf5" : "transparent" }}>
                          <td style={styles.td}>
                            <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                              <span style={styles.avatar}>{c.nombres[0]}{c.apellidos[0]}</span>
                              <div style={{ fontWeight: 500 }}>{c.nombres} {c.apellidos}</div>
                            </div>
                          </td>
                          <td style={styles.td}>{c.dni}</td>
                          <td style={styles.td}>{c.numero_licencia}</td>
                          <td style={styles.td}>{c.tipo_licencia}</td>
                          <td style={styles.td}>
                            <span style={{ color: licA ? "#791F1F" : "#222", fontWeight: licA ? 600 : 400 }}>
                              {c.fec_vence_licencia}
                              {licA && <span style={styles.alertBadge}>{diasLic < 0 ? "VENCIDA" : `${diasLic}d`}</span>}
                            </span>
                          </td>
                          <td style={styles.td}>
                            <span style={{ color: certA ? "#791F1F" : "#222", fontWeight: certA ? 600 : 400 }}>
                              {c.fec_vence_certif_prot}
                              {certA && <span style={styles.alertBadge}>{diasCert < 0 ? "VENCIDA" : `${diasCert}d`}</span>}
                            </span>
                          </td>
                          <td style={styles.td}>
                            {user?.role === "admin_atu" ? (
                              <select
                                value={c.estado}
                                onChange={async e => {
                                  const nuevo = e.target.value;
                                  try {
                                    await api.patch(`/api/choferes/${c.id}/estado`, { estado: nuevo });
                                    setChoferes(prev => prev.map(x => x.id === c.id ? { ...x, estado: nuevo } : x));
                                  } catch { /* el servidor rechaza si el valor no es válido */ }
                                }}
                                style={{ ...styles.tag, background: est.bg, color: est.color, border: "none", cursor: "pointer", fontWeight: 500 }}
                              >
                                {["activo","suspendido","licencia_medica","vacaciones","inactivo"].map(s => (
                                  <option key={s} value={s}>{s.replaceAll("_", " ")}</option>
                                ))}
                              </select>
                            ) : (
                              <span style={{ ...styles.tag, background: est.bg, color: est.color }}>
                                {c.estado.replaceAll("_", " ")}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <div style={styles.footer}>{choferes.length} choferes</div>
              </div>
            )}
          </>
        )}

        {/* ─── Tab Disponibilidad ─── */}
        {tab === "disponibilidad" && (
          <>
            <div>
              <select value={filtroChofer} onChange={e => setFiltroChofer(e.target.value)} style={styles.select}>
                <option value="">Todos los choferes</option>
                {choferes.map(c => (
                  <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>
                ))}
              </select>
            </div>
            <div style={styles.tableWrap}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {["Chofer","Fecha","Desde","Hasta","Motivo","Obs.",""].map(h => (
                      <th key={h} style={styles.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {disponibilidades.length === 0 && (
                    <tr>
                      <td colSpan={7} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                        Sin registros de indisponibilidad.
                      </td>
                    </tr>
                  )}
                  {disponibilidades.map(d => {
                    const ms = MOTIVO_STYLE[d.motivo] ?? MOTIVO_STYLE.otro;
                    return (
                      <tr key={d.id}>
                        <td style={styles.td}>{choferNombre(d.chofer_id)}</td>
                        <td style={styles.td}>{d.fecha}</td>
                        <td style={styles.td}>{d.hora_desde}</td>
                        <td style={styles.td}>{d.hora_hasta}</td>
                        <td style={styles.td}>
                          <span style={{ ...styles.tag, background: ms.bg, color: ms.color }}>
                            {d.motivo}
                          </span>
                        </td>
                        <td style={styles.td}>{d.observaciones ?? "—"}</td>
                        <td style={styles.td}>
                          {user?.role === "admin_atu" && (
                            <button onClick={() => handleEliminarDisp(d.id)}
                              style={{ ...styles.btnSecondary, fontSize: 11, padding: "3px 8px", color: "#791F1F", borderColor: "#F7C1C1" }}>
                              Eliminar
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <div style={styles.footer}>{disponibilidades.length} registros</div>
            </div>
          </>
        )}
      </main>

      {/* Modal registrar chofer */}
      {modal && (
        <div style={styles.overlay} onClick={() => setModal(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Registrar chofer</h2>
            <form onSubmit={handleRegistrar} style={styles.form}>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Nombres" style={{ flex: 1 }}>
                  <input name="nombres" value={form.nombres} onChange={handleField}
                    placeholder="Carlos Alberto" style={styles.input} />
                </Field>
                <Field label="Apellidos" style={{ flex: 1 }}>
                  <input name="apellidos" value={form.apellidos} onChange={handleField}
                    placeholder="Ramírez Torres" style={styles.input} />
                </Field>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="DNI (8 dígitos)" style={{ flex: 1 }}>
                  <input name="dni" value={form.dni} onChange={handleField}
                    placeholder="12345678" maxLength={8} style={styles.input} />
                </Field>
                <Field label="Fecha nacimiento" style={{ flex: 1 }}>
                  <input type="date" name="fecha_nacimiento" value={form.fecha_nacimiento}
                    onChange={handleField} style={styles.input} />
                </Field>
              </div>
              <Field label="Correo (acceso al portal)">
                <input type="email" name="email" value={form.email} onChange={handleField}
                  placeholder="opcional — si no se indica, se usará el DNI@metrohub.gob.pe"
                  style={styles.input} />
              </Field>
              <Field label="Área">
                <select name="area_id" value={form.area_id}
                  onChange={handleField} style={styles.input}>
                  <option value="">— Seleccionar —</option>
                  {areas.map(c => (
                    <option key={c.id} value={c.id}>{c.nombre_corto} — {c.ruc}</option>
                  ))}
                </select>
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="N° licencia" style={{ flex: 1 }}>
                  <input name="numero_licencia" value={form.numero_licencia}
                    onChange={handleField} placeholder="Q12345678" style={styles.input} />
                </Field>
                <Field label="Tipo licencia" style={{ flex: 1 }}>
                  <select name="tipo_licencia" value={form.tipo_licencia}
                    onChange={handleField} style={styles.input}>
                    <option value="A-IIIA">A-IIIA</option>
                    <option value="A-IIIB">A-IIIB</option>
                    <option value="A-IIIC">A-IIIC</option>
                  </select>
                </Field>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Vence licencia" style={{ flex: 1 }}>
                  <input type="date" name="fec_vence_licencia" value={form.fec_vence_licencia}
                    onChange={handleField} style={styles.input} />
                </Field>
                <Field label="Vence certif. protección" style={{ flex: 1 }}>
                  <input type="date" name="fec_vence_certif_prot" value={form.fec_vence_certif_prot}
                    onChange={handleField} style={styles.input} />
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

      {/* Modal registrar indisponibilidad */}
      {modalDisp && (
        <div style={styles.overlay} onClick={() => setModalDisp(false)}>
          <div style={{ ...styles.modal, width: 460 }} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Registrar indisponibilidad</h2>
            <form onSubmit={handleRegistrarDisp} style={styles.form}>
              <Field label="Chofer *">
                <select value={formDisp.chofer_id}
                  onChange={e => setFormDisp(f => ({ ...f, chofer_id: e.target.value }))}
                  style={styles.input}>
                  <option value="">— Seleccionar —</option>
                  {choferes.filter(c => c.estado === "activo").map(c => (
                    <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>
                  ))}
                </select>
              </Field>
              <Field label="Fecha *">
                <input type="date" value={formDisp.fecha}
                  onChange={e => setFormDisp(f => ({ ...f, fecha: e.target.value }))}
                  style={styles.input} />
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Hora desde *" style={{ flex: 1 }}>
                  <input type="time" value={formDisp.hora_desde}
                    onChange={e => setFormDisp(f => ({ ...f, hora_desde: e.target.value }))}
                    style={styles.input} />
                </Field>
                <Field label="Hora hasta *" style={{ flex: 1 }}>
                  <input type="time" value={formDisp.hora_hasta}
                    onChange={e => setFormDisp(f => ({ ...f, hora_hasta: e.target.value }))}
                    style={styles.input} />
                </Field>
              </div>
              <Field label="Motivo *">
                <select value={formDisp.motivo}
                  onChange={e => setFormDisp(f => ({ ...f, motivo: e.target.value }))}
                  style={styles.input}>
                  <option value="descanso">Descanso</option>
                  <option value="vacaciones">Vacaciones</option>
                  <option value="medico">Médico</option>
                  <option value="capacitacion">Capacitación</option>
                  <option value="personal">Personal</option>
                  <option value="otro">Otro</option>
                </select>
              </Field>
              <Field label="Observaciones">
                <textarea value={formDisp.observaciones}
                  onChange={e => setFormDisp(f => ({ ...f, observaciones: e.target.value }))}
                  style={{ ...styles.input, height: 60, resize: "vertical" }}
                  placeholder="Opcional" />
              </Field>
              {dispErr && <div style={styles.formErr}>{dispErr}</div>}
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModalDisp(false); setDispErr(""); setFormDisp(DISP_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={dispSaving}>
                  {dispSaving ? "Guardando…" : "Registrar"}
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
  tabs:       { display: "flex", gap: 4, borderBottom: "1px solid #e8e8e8", paddingBottom: 0 },
  tab:        { padding: "8px 18px", borderRadius: "6px 6px 0 0", border: "none", background: "transparent", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", cursor: "pointer" },
  tabActive:  { background: "#fff", color: "#185FA5", fontWeight: 600, borderBottom: "2px solid #185FA5" },
  btnPrimary: { padding: "8px 18px", borderRadius: 8, border: "none", background: "#185FA5", fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer" },
  btnSecondary:{ padding: "8px 16px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444", cursor: "pointer" },
  select:     { fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#222", outline: "none" },
  tableWrap:  { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:      { width: "100%", borderCollapse: "collapse" },
  th:         { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:         { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:        { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  avatar:     { width: 30, height: 30, borderRadius: "50%", background: "#B5D4F4", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: "#0C447C", flexShrink: 0 },
  alertBadge: { marginLeft: 6, background: "#FCEBEB", color: "#791F1F", fontSize: 10, fontWeight: 700, padding: "1px 6px", borderRadius: 4 },
  footer:     { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:      { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:   { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 490, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
