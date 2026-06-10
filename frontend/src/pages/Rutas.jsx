import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TIPO_COLOR = {
  regular:  { bg: "#E6F1FB", color: "#0C447C" },
  expreso:  { bg: "#EAF3DE", color: "#27500A" },
  nocturna: { bg: "#F3E6FB", color: "#4A0C7C" },
};
const TRAMO_COLOR = {
  norte:  { bg: "#E6F1FB", color: "#0C447C" },
  centro: { bg: "#FAEEDA", color: "#633806" },
  sur:    { bg: "#EAF3DE", color: "#27500A" },
};
const TIPO_EST = {
  terminal:     { bg: "#FCEBEB", color: "#791F1F" },
  intermedia:   { bg: "#F0F0F0", color: "#555"    },
  transferencia:{ bg: "#F3E6FB", color: "#4A0C7C" },
};

const FORM_RUTA_INIT = {
  codigo: "", nombre: "", tipo: "regular",
  hora_inicio: "05:00", hora_fin: "23:00", frecuencia_min: 10,
};
const FORM_EST_INIT = {
  codigo: "", nombre: "", tipo: "intermedia", tramo: "norte",
  orden_troncal: "", latitud: "", longitud: "",
};
const FORM_ASIG_INIT = { estacion_id: "", orden: "", tiempo_est_min: "" };

export default function Rutas({ user, onNav, onLogout }) {
  const [rutas, setRutas]           = useState([]);
  const [estaciones, setEstaciones] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [tab, setTab]               = useState("rutas");

  // Modales rutas
  const [modalRuta, setModalRuta]   = useState(false);
  const [editRuta, setEditRuta]     = useState(null); // null = crear, objeto = editar
  const [formRuta, setFormRuta]     = useState(FORM_RUTA_INIT);
  const [submittingR, setSubmR]     = useState(false);
  const [formErrR, setFormErrR]     = useState("");

  // Modales estaciones
  const [modalEst, setModalEst]     = useState(false);
  const [formEst, setFormEst]       = useState(FORM_EST_INIT);
  const [submittingE, setSubmE]     = useState(false);
  const [formErrE, setFormErrE]     = useState("");

  // Modal recorrido de ruta
  const [rutaRecorrido, setRutaRec] = useState(null); // ruta objeto
  const [recorrido, setRecorrido]   = useState([]);
  const [loadRec, setLoadRec]       = useState(false);
  const [formAsig, setFormAsig]     = useState(FORM_ASIG_INIT);
  const [asigErr, setAsigErr]       = useState("");
  const [asigSaving, setAsigSaving] = useState(false);

  const isAdmin = user?.role === "admin_atu";

  useEffect(() => {
    Promise.all([
      api.get("/api/rutas"),
      api.get("/api/estaciones"),
    ])
      .then(([r, e]) => {
        setRutas(r);
        setEstaciones(e.estaciones ?? []);
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  const abrirRecorrido = async (ruta) => {
    setRutaRec(ruta);
    setRecorrido([]);
    setLoadRec(true);
    setFormAsig(FORM_ASIG_INIT);
    setAsigErr("");
    try {
      const data = await api.get(`/api/rutas/${ruta.id}/estaciones`);
      setRecorrido(data);
    } catch { setRecorrido([]); }
    finally { setLoadRec(false); }
  };

  const handleAsignarEst = async (e) => {
    e.preventDefault();
    setAsigErr("");
    if (!formAsig.estacion_id || !formAsig.orden) {
      setAsigErr("Estación y orden son obligatorios.");
      return;
    }
    setAsigSaving(true);
    try {
      const nuevas = await api.post(`/api/rutas/${rutaRecorrido.id}/estaciones`, {
        estacion_id:    Number(formAsig.estacion_id),
        orden:          Number(formAsig.orden),
        tiempo_est_min: formAsig.tiempo_est_min ? Number(formAsig.tiempo_est_min) : null,
      });
      setRecorrido(nuevas);
      setFormAsig(FORM_ASIG_INIT);
    } catch (e) {
      setAsigErr(e.message || "No se pudo asignar la estación.");
    } finally {
      setAsigSaving(false);
    }
  };

  const handleDesasignar = async (estacion_id) => {
    try {
      await api.delete(`/api/rutas/${rutaRecorrido.id}/estaciones/${estacion_id}`);
      setRecorrido(prev => prev.filter(r => r.estacion_id !== estacion_id));
    } catch (e) {
      alert(e.message || "No se pudo eliminar.");
    }
  };

  const abrirEditarRuta = (ruta) => {
    setEditRuta(ruta);
    setFormRuta({
      codigo:        ruta.codigo,
      nombre:        ruta.nombre,
      tipo:          ruta.tipo,
      hora_inicio:   ruta.hora_inicio,
      hora_fin:      ruta.hora_fin,
      frecuencia_min: String(ruta.frecuencia_min),
    });
    setFormErrR("");
    setModalRuta(true);
  };

  const handleCrearRuta = async (e) => {
    e.preventDefault();
    setFormErrR("");
    if (!formRuta.codigo.trim() || !formRuta.nombre.trim()) {
      setFormErrR("Código y nombre son obligatorios.");
      return;
    }
    setSubmR(true);
    try {
      const payload = { ...formRuta, frecuencia_min: Number(formRuta.frecuencia_min) };
      if (editRuta) {
        const actualizada = await api.put(`/api/rutas/${editRuta.id}`, payload);
        setRutas(prev => prev.map(r => r.id === editRuta.id ? actualizada : r));
      } else {
        const nueva = await api.post("/api/rutas", payload);
        setRutas(prev => [...prev, nueva]);
      }
      setModalRuta(false);
      setEditRuta(null);
      setFormRuta(FORM_RUTA_INIT);
    } catch (e) {
      setFormErrR(e.message || (editRuta ? "No se pudo actualizar la ruta." : "No se pudo crear la ruta."));
    } finally {
      setSubmR(false);
    }
  };

  const handleToggleEstadoRuta = async (ruta) => {
    try {
      const res = await api.patch(`/api/rutas/${ruta.id}/estado?activa=${!ruta.activa}`);
      setRutas(prev => prev.map(r => r.id === ruta.id ? { ...r, activa: res.ruta?.activa ?? !ruta.activa } : r));
    } catch (e) {
      alert(e.message || "No se pudo cambiar el estado de la ruta.");
    }
  };

  const handleCrearEst = async (e) => {
    e.preventDefault();
    setFormErrE("");
    if (!formEst.codigo.trim() || !formEst.nombre.trim()) {
      setFormErrE("Código y nombre son obligatorios.");
      return;
    }
    setSubmE(true);
    try {
      const nueva = await api.post("/api/estaciones", {
        ...formEst,
        orden_troncal: formEst.orden_troncal ? Number(formEst.orden_troncal) : null,
        latitud:       formEst.latitud       ? Number(formEst.latitud)       : null,
        longitud:      formEst.longitud      ? Number(formEst.longitud)      : null,
      });
      setEstaciones(prev => [...prev, nueva]);
      setModalEst(false);
      setFormEst(FORM_EST_INIT);
    } catch (e) {
      setFormErrE(e.message || "No se pudo crear la estación.");
    } finally {
      setSubmE(false);
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
            {isAdmin && tab === "rutas" && (
              <button style={styles.btnPrimary} onClick={() => { setEditRuta(null); setFormRuta(FORM_RUTA_INIT); setFormErrR(""); setModalRuta(true); }}>
                + Nueva ruta
              </button>
            )}
            {isAdmin && tab === "estaciones" && (
              <button style={styles.btnPrimary} onClick={() => setModalEst(true)}>+ Nueva estación</button>
            )}
            <div style={styles.badge}>{isAdmin ? "Admin ATU" : "Supervisor"}</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={styles.tabs}>
          {["rutas","estaciones"].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ ...styles.tab, ...(tab === t ? styles.tabActive : {}) }}>
              {t === "rutas" ? "Rutas" : "Estaciones"}
            </button>
          ))}
        </div>

        {loading && <div style={styles.empty}>Cargando…</div>}
        {error   && <div style={styles.errorBox}>Error al cargar: {error}</div>}

        {/* ─── Tab Rutas ─── */}
        {!loading && !error && tab === "rutas" && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Código","Nombre","Tipo","Horario","Frecuencia","Estado",""].map(h => (
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
                        <span style={{ ...styles.tag, background: tc.bg, color: tc.color }}>{r.tipo}</span>
                      </td>
                      <td style={styles.td}>{r.hora_inicio} – {r.hora_fin}</td>
                      <td style={styles.td}>Cada {r.frecuencia_min} min</td>
                      <td style={styles.td}>
                        {isAdmin ? (
                          <button
                            onClick={() => handleToggleEstadoRuta(r)}
                            style={{
                              ...styles.tag,
                              background: r.activa ? "#EAF3DE" : "#f0f0f0",
                              color: r.activa ? "#27500A" : "#888",
                              border: r.activa ? "1px solid #C0DD97" : "1px solid #e0e0e0",
                              cursor: "pointer",
                            }}
                            title={r.activa ? "Clic para desactivar" : "Clic para activar"}
                          >
                            {r.activa ? "Activa" : "Inactiva"}
                          </button>
                        ) : (
                          <span style={{ ...styles.tag, background: r.activa ? "#EAF3DE" : "#f0f0f0", color: r.activa ? "#27500A" : "#888" }}>
                            {r.activa ? "Activa" : "Inactiva"}
                          </span>
                        )}
                      </td>
                      <td style={styles.td}>
                        <div style={{ display: "flex", gap: 6 }}>
                          <button onClick={() => abrirRecorrido(r)}
                            style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}>
                            Recorrido
                          </button>
                          {isAdmin && (
                            <button onClick={() => abrirEditarRuta(r)}
                              style={{ ...styles.btnSecondary, fontSize: 11, padding: "4px 10px" }}>
                              Editar
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{rutas.length} rutas en total</div>
          </div>
        )}

        {/* ─── Tab Estaciones ─── */}
        {!loading && !error && tab === "estaciones" && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {["Código","Nombre","Tipo","Tramo","Orden troncal","Estado"].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {estaciones.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                      Sin estaciones registradas.
                    </td>
                  </tr>
                )}
                {estaciones.map(e => {
                  const tp = TIPO_EST[e.tipo]     ?? { bg: "#f0f0f0", color: "#555" };
                  const tr = TRAMO_COLOR[e.tramo] ?? { bg: "#f0f0f0", color: "#555" };
                  return (
                    <tr key={e.id}>
                      <td style={styles.td}>
                        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: 12, fontWeight: 600 }}>
                          {e.codigo}
                        </span>
                      </td>
                      <td style={styles.td}>{e.nombre}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: tp.bg, color: tp.color }}>{e.tipo}</span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: tr.bg, color: tr.color }}>{e.tramo}</span>
                      </td>
                      <td style={styles.td}>{e.orden_troncal ?? "—"}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.tag, background: e.activa ? "#EAF3DE" : "#f0f0f0", color: e.activa ? "#27500A" : "#888" }}>
                          {e.activa ? "Activa" : "Inactiva"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={styles.footer}>{estaciones.length} estaciones en total</div>
          </div>
        )}
      </main>

      {/* Modal nueva / editar ruta */}
      {modalRuta && (
        <div style={styles.overlay} onClick={() => { setModalRuta(false); setEditRuta(null); setFormErrR(""); setFormRuta(FORM_RUTA_INIT); }}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>{editRuta ? `Editar ruta — ${editRuta.codigo}` : "Nueva ruta"}</h2>
            <form onSubmit={handleCrearRuta} style={styles.form}>
              <Field label="Código">
                <input name="codigo" value={formRuta.codigo}
                  onChange={e => setFormRuta(f => ({ ...f, codigo: e.target.value }))}
                  placeholder="ej. SIT-1" style={styles.input} maxLength={20}
                  disabled={!!editRuta} />
              </Field>
              <Field label="Nombre">
                <input name="nombre" value={formRuta.nombre}
                  onChange={e => setFormRuta(f => ({ ...f, nombre: e.target.value }))}
                  placeholder="ej. Naranjal - Matellini" style={styles.input} />
              </Field>
              <Field label="Tipo">
                <select value={formRuta.tipo} onChange={e => setFormRuta(f => ({ ...f, tipo: e.target.value }))} style={styles.input}>
                  <option value="regular">Regular</option>
                  <option value="expreso">Expreso</option>
                  <option value="nocturna">Nocturna</option>
                </select>
              </Field>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Hora inicio" style={{ flex: 1 }}>
                  <input type="time" value={formRuta.hora_inicio}
                    onChange={e => setFormRuta(f => ({ ...f, hora_inicio: e.target.value }))} style={styles.input} />
                </Field>
                <Field label="Hora fin" style={{ flex: 1 }}>
                  <input type="time" value={formRuta.hora_fin}
                    onChange={e => setFormRuta(f => ({ ...f, hora_fin: e.target.value }))} style={styles.input} />
                </Field>
              </div>
              <Field label="Frecuencia (min)">
                <input type="number" value={formRuta.frecuencia_min}
                  onChange={e => setFormRuta(f => ({ ...f, frecuencia_min: e.target.value }))}
                  min={2} max={60} style={styles.input} />
              </Field>
              {formErrR && <div style={styles.formErr}>{formErrR}</div>}
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModalRuta(false); setEditRuta(null); setFormErrR(""); setFormRuta(FORM_RUTA_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submittingR}>
                  {submittingR ? "Guardando…" : editRuta ? "Guardar cambios" : "Crear ruta"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal nueva estación */}
      {modalEst && (
        <div style={styles.overlay} onClick={() => setModalEst(false)}>
          <div style={styles.modal} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nueva estación</h2>
            <form onSubmit={handleCrearEst} style={styles.form}>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Código *" style={{ flex: 1 }}>
                  <input value={formEst.codigo}
                    onChange={e => setFormEst(f => ({ ...f, codigo: e.target.value }))}
                    placeholder="Ej. EST-001" style={styles.input} maxLength={20} />
                </Field>
                <Field label="Nombre *" style={{ flex: 2 }}>
                  <input value={formEst.nombre}
                    onChange={e => setFormEst(f => ({ ...f, nombre: e.target.value }))}
                    placeholder="Ej. Estación Naranjal" style={styles.input} />
                </Field>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Tipo *" style={{ flex: 1 }}>
                  <select value={formEst.tipo}
                    onChange={e => setFormEst(f => ({ ...f, tipo: e.target.value }))} style={styles.input}>
                    <option value="terminal">Terminal</option>
                    <option value="intermedia">Intermedia</option>
                    <option value="transferencia">Transferencia</option>
                  </select>
                </Field>
                <Field label="Tramo *" style={{ flex: 1 }}>
                  <select value={formEst.tramo}
                    onChange={e => setFormEst(f => ({ ...f, tramo: e.target.value }))} style={styles.input}>
                    <option value="norte">Norte</option>
                    <option value="centro">Centro</option>
                    <option value="sur">Sur</option>
                  </select>
                </Field>
                <Field label="Orden troncal" style={{ flex: 1 }}>
                  <input type="number" value={formEst.orden_troncal}
                    onChange={e => setFormEst(f => ({ ...f, orden_troncal: e.target.value }))}
                    placeholder="Ej. 1" min={1} style={styles.input} />
                </Field>
              </div>
              {formErrE && <div style={styles.formErr}>{formErrE}</div>}
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setModalEst(false); setFormErrE(""); setFormEst(FORM_EST_INIT); }}>
                  Cancelar
                </button>
                <button type="submit" style={styles.btnPrimary} disabled={submittingE}>
                  {submittingE ? "Creando…" : "Crear estación"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal recorrido de ruta */}
      {rutaRecorrido && (
        <div style={styles.overlay} onClick={() => setRutaRec(null)}>
          <div style={{ ...styles.modal, width: 560 }} onClick={e => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>
              Recorrido — {rutaRecorrido.codigo}
              <span style={{ fontWeight: 400, fontSize: 14, color: "#888", marginLeft: 10 }}>
                {rutaRecorrido.nombre}
              </span>
            </h2>

            {loadRec
              ? <div style={{ color: "#888", fontSize: 13 }}>Cargando…</div>
              : recorrido.length === 0
                ? <div style={{ color: "#aaa", fontSize: 13, marginBottom: 16 }}>Sin estaciones asignadas.</div>
                : (
                  <table style={{ ...styles.table, marginBottom: 16 }}>
                    <thead>
                      <tr>
                        {["Ord.","Código","Nombre","Tramo","Tiempo",""].map(h => (
                          <th key={h} style={{ ...styles.th, padding: "7px 10px" }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {recorrido.map(r => (
                        <tr key={r.estacion_id}>
                          <td style={{ ...styles.td, padding: "7px 10px" }}>
                            <strong>{r.orden}</strong>
                          </td>
                          <td style={{ ...styles.td, padding: "7px 10px", fontFamily: "'Space Mono',monospace", fontSize: 11 }}>
                            {r.codigo}
                          </td>
                          <td style={{ ...styles.td, padding: "7px 10px" }}>{r.nombre}</td>
                          <td style={{ ...styles.td, padding: "7px 10px" }}>{r.tramo}</td>
                          <td style={{ ...styles.td, padding: "7px 10px" }}>
                            {r.tiempo_est_min ? `${r.tiempo_est_min} min` : "—"}
                          </td>
                          <td style={{ ...styles.td, padding: "7px 10px" }}>
                            {isAdmin && (
                              <button onClick={() => handleDesasignar(r.estacion_id)}
                                style={{ ...styles.btnSecondary, fontSize: 11, padding: "3px 8px", color: "#791F1F", borderColor: "#F7C1C1" }}>
                                Quitar
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
            }

            {isAdmin && (
              <form onSubmit={handleAsignarEst} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-end" }}>
                <Field label="Estación" style={{ flex: 2, minWidth: 160 }}>
                  <select value={formAsig.estacion_id}
                    onChange={e => setFormAsig(f => ({ ...f, estacion_id: e.target.value }))}
                    style={{ ...styles.input, fontSize: 12 }}>
                    <option value="">— Seleccionar —</option>
                    {estaciones.map(e => (
                      <option key={e.id} value={e.id}>{e.codigo} — {e.nombre}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Orden" style={{ flex: 1, minWidth: 70 }}>
                  <input type="number" value={formAsig.orden}
                    onChange={e => setFormAsig(f => ({ ...f, orden: e.target.value }))}
                    placeholder="1" min={1} style={{ ...styles.input, fontSize: 12 }} />
                </Field>
                <Field label="Tiempo (min)" style={{ flex: 1, minWidth: 80 }}>
                  <input type="number" value={formAsig.tiempo_est_min}
                    onChange={e => setFormAsig(f => ({ ...f, tiempo_est_min: e.target.value }))}
                    placeholder="Opt." min={1} style={{ ...styles.input, fontSize: 12 }} />
                </Field>
                <button type="submit" style={{ ...styles.btnPrimary, height: 38, alignSelf: "flex-end" }}
                  disabled={asigSaving}>
                  {asigSaving ? "…" : "Agregar"}
                </button>
              </form>
            )}
            {asigErr && <div style={{ ...styles.formErr, marginTop: 8 }}>{asigErr}</div>}

            <div style={{ marginTop: 20, textAlign: "right" }}>
              <button style={styles.btnSecondary} onClick={() => setRutaRec(null)}>Cerrar</button>
            </div>
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
  tableWrap:  { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:      { width: "100%", borderCollapse: "collapse" },
  th:         { fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888", padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left", background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px" },
  td:         { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222", padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "middle" },
  tag:        { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  footer:     { fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#aaa", padding: "10px 14px", textAlign: "right" },
  empty:      { fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#888", padding: 20, textAlign: "center" },
  errorBox:   { background: "#FCEBEB", border: "0.5px solid #F7C1C1", borderRadius: 8, padding: "12px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#791F1F" },
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:      { background: "#fff", borderRadius: 12, padding: 28, width: 440, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.18)" },
  modalTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 600, color: "#111", marginBottom: 20 },
  form:       { display: "flex", flexDirection: "column", gap: 14 },
  input:      { fontSize: 13, padding: "9px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#f8f9fb", color: "#111", outline: "none", width: "100%", boxSizing: "border-box" },
  formErr:    { background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6, padding: "8px 12px", fontSize: 12, color: "#791F1F" },
};
