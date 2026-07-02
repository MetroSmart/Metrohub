import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { api } from "../api";

const TURNO_STYLE = {
  manana: { background: "#E6F1FB", color: "#0C447C" },
  tarde:  { background: "#FAEEDA", color: "#633806" },
  noche:  { background: "#F3E6FB", color: "#4A0C7C" },
};
const TURNO_LABEL = { manana: "Mañana", tarde: "Tarde", noche: "Noche" };

const SEV_STYLE = {
  alta:    { background: "#FCEBEB", color: "#791F1F", border: "1px solid #F7C1C1" },
  media:   { background: "#FAEEDA", color: "#633806", border: "1px solid #F0D1A0" },
  baja:    { background: "#FFF8E1", color: "#7A5800", border: "1px solid #F0D87A" },
  critica: { background: "#F5E6FF", color: "#5A0B8E", border: "1px solid #D6B3F7" },
};

const ESTADO_BADGE = {
  borrador:  { background: "#F0F0F0", color: "#555" },
  revision:  { background: "#FAEEDA", color: "#633806" },
  aprobada:  { background: "#EAF3DE", color: "#27500A" },
  archivada: { background: "#E8E8E8", color: "#888" },
};

const emptyForm = { nombre: "", fecha_inicio: "", fecha_fin: "", observaciones: "" };

const GUIA_POR_TIPO = {
  descanso_insuficiente:  "Revisa los dos turnos consecutivos y cancela o reprograma el que tenga menor prioridad. Asegúrate de que el chofer tenga al menos 8 horas de descanso entre el fin de un turno y el inicio del siguiente.",
  solapamiento_turno:     "Identifica las dos asignaciones superpuestas. Cancela la de menor prioridad y busca un chofer disponible en el área como reemplazo para cubrir ese horario.",
  exceso_8h_dia:          "El chofer supera las 8 horas diarias permitidas. Reasigna uno de los turnos del día a otro chofer disponible en el área o ajusta la duración estimada si hay un error de registro.",
  chofer_no_disponible:   "El chofer tiene una indisponibilidad registrada para esta fecha. Verifica el motivo en el módulo de disponibilidades y asigna un reemplazo del área que esté libre.",
  licencia_vencida:       "La licencia de conducir está vencida — el chofer no puede operar. Cancela la asignación y busca un reemplazo activo con licencia vigente. Notifica al chofer para que inicie el trámite de renovación.",
  certif_prot_vencida:    "El certificado de protocolos está vencido. Suspende temporalmente las asignaciones del chofer hasta que renueve el certificado. Coordina el reemplazo con el supervisor del área.",
  area_incorrecta:        "La asignación está en un área que no corresponde al chofer. Reasigna a un chofer del área correcta o coordina con el supervisor para autorizar la asignación cruzada si es necesario.",
  bus_no_operativo:       "El bus asignado no está operativo. Asigna otro bus disponible del mismo tipo en el área o deja el campo sin bus si el chofer puede incorporarse a una unidad ya disponible en ruta.",
  otro:                   "Revisa el caso con el supervisor del área y aplica el protocolo interno correspondiente. Documenta las acciones tomadas en las observaciones de la asignación.",
};

export default function Grilla({ user, onNav, onLogout, initialFecha, onSugerirReemplazo }) {
  const [horarios, setHorarios]             = useState([]);
  const [rutas, setRutas]                   = useState([]);
  const [programaciones, setProgramaciones] = useState([]);
  const [rutaId, setRutaId]                 = useState("");
  const [fecha, setFecha]                   = useState(initialFecha || new Date().toISOString().slice(0, 10));
  const [selectedProgId, setSelectedProgId] = useState("");
  const [loading, setLoading]               = useState(true);
  const [actionStatus, setActionStatus]     = useState(null);
  const [saving, setSaving]                 = useState(false);
  const [approving, setApproving]           = useState(false);
  const [resolving, setResolving]           = useState(null);
  const [resolverModal, setResolverModal]   = useState(null);
  const [duplicating, setDuplicating]       = useState(false);

  // Modal nueva programación
  const [showModal, setShowModal]   = useState(false);
  const [formProg, setFormProg]     = useState(emptyForm);
  const [formErr, setFormErr]       = useState("");
  const [formSaving, setFormSaving] = useState(false);

  // Modal duplicar semana
  const [showDupModal, setShowDupModal] = useState(false);
  const [dupForm, setDupForm]           = useState({ origen: "", destino: "" });
  const [dupErr, setDupErr]             = useState("");
  const [dupResult, setDupResult]       = useState(null);

  // Modal agregar horario (admin only)
  const [showHorarioModal, setShowHorarioModal]   = useState(false);
  const [formHorario, setFormHorario]             = useState({ ruta_id: "", fecha: "", hora_salida: "", turno: "manana", duracion_est_min: 60 });
  const [formHorarioErr, setFormHorarioErr]       = useState("");
  const [formHorarioSaving, setFormHorarioSaving] = useState(false);

  // Modal asignar chofer (admin o supervisor de área)
  const [asigTarget, setAsigTarget]         = useState(null); // horario seleccionado
  const [asigChoferes, setAsigChoferes]     = useState([]);
  const [asigConcs, setAsigConcs]           = useState([]);
  const [asigBuses, setAsigBuses]           = useState([]);
  const [formAsig, setFormAsig]             = useState({ chofer_id: "", area_id: "", bus_placa: "", notas: "" });
  const [formAsigErr, setFormAsigErr]       = useState("");
  const [formAsigSaving, setFormAsigSaving] = useState(false);

  useEffect(() => {
    if (initialFecha) setFecha(initialFecha);
  }, [initialFecha]);

  useEffect(() => {
    api.get("/api/rutas?solo_activas=true").then(setRutas).catch(() => {});
    api.get("/api/programaciones?limit=100")
      .then(d => {
        const lista = d.programaciones ?? [];
        setProgramaciones(lista);
        if (lista.length > 0 && !selectedProgId) {
          const hoy = new Date().toISOString().slice(0, 10);
          const vigente = lista.find(p => p.fecha_inicio <= hoy && p.fecha_fin >= hoy);
          const proxima = [...lista].sort((a, b) => a.fecha_inicio.localeCompare(b.fecha_inicio))
                            .find(p => p.fecha_inicio > hoy);
          const elegida = vigente || proxima || lista[0];
          setSelectedProgId(String(elegida.id));
          if (hoy < elegida.fecha_inicio || hoy > elegida.fecha_fin) {
            setFecha(elegida.fecha_inicio);
          }
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (fecha)         params.set("fecha",          fecha);
    if (rutaId)        params.set("ruta_id",        rutaId);
    if (selectedProgId) params.set("programacion_id", selectedProgId);
    api.get(`/api/horarios?${params}`)
      .then(d => {
        setHorarios(d.horarios ?? []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [fecha, rutaId, selectedProgId]);

  const programacionId = selectedProgId ? Number(selectedProgId) : null;

  const abrirAsignar = async (horario) => {
    setAsigTarget(horario);
    setFormAsig({ chofer_id: "", area_id: user?.role === "supervisor_area" ? String(user.area_id) : "", bus_placa: "", notas: "" });
    setFormAsigErr("");
    const areaParam = user?.role === "supervisor_area" && user.area_id
      ? `&area_id=${user.area_id}` : "";
    const [ch, co, bu] = await Promise.all([
      api.get(`/api/choferes?estado=activo${areaParam}`).catch(() => []),
      api.get("/api/areas").catch(() => ({ areas: [] })),
      api.get(`/api/buses?estado=operativo${areaParam}`).catch(() => ({ buses: [] })),
    ]);
    const choferes = Array.isArray(ch) ? ch : (ch.choferes ?? ch);
    setAsigChoferes(
      user?.role === "supervisor_area" && user.area_id
        ? choferes.filter(c => c.area_id === user.area_id)
        : choferes,
    );
    setAsigConcs(co.areas ?? co);
    const buses = bu.buses ?? bu;
    setAsigBuses(
      user?.role === "supervisor_area" && user.area_id
        ? buses.filter(b => b.area_id === user.area_id)
        : buses,
    );
  };

  const handleCrearAsignacion = async (e) => {
    e.preventDefault();
    setFormAsigErr("");
    if (!formAsig.chofer_id || !formAsig.area_id) {
      setFormAsigErr("Chofer y área son obligatorios.");
      return;
    }
    setFormAsigSaving(true);
    try {
      await api.post("/api/horarios/asignaciones", {
        horario_id:       asigTarget.id,
        chofer_id:        Number(formAsig.chofer_id),
        area_id: Number(formAsig.area_id),
        bus_placa:        formAsig.bus_placa || null,
        notas:            formAsig.notas || null,
      });
      const params = new URLSearchParams();
      if (fecha)          params.set("fecha",           fecha);
      if (rutaId)         params.set("ruta_id",         rutaId);
      if (selectedProgId) params.set("programacion_id", selectedProgId);
      api.get(`/api/horarios?${params}`).then(d => setHorarios(d.horarios ?? []));
      setAsigTarget(null);
    } catch (err) {
      setFormAsigErr(err.message || "No se pudo crear la asignación.");
    } finally {
      setFormAsigSaving(false);
    }
  };

  const handleEliminarProg = async () => {
    if (!progActual) return;
    if (!window.confirm(`¿Eliminar la programación "${progActual.nombre}"? Se eliminarán todos sus horarios y asignaciones.`)) return;
    try {
      await api.delete(`/api/programaciones/${progActual.id}`);
      setProgramaciones(prev => prev.filter(p => p.id !== progActual.id));
      setSelectedProgId("");
      setHorarios([]);
    } catch (err) {
      alert(err.message || "No se pudo eliminar la programación.");
    }
  };

  const handleCrearHorario = async (e) => {
    e.preventDefault();
    setFormHorarioErr("");
    if (!formHorario.ruta_id || !formHorario.fecha || !formHorario.hora_salida) {
      setFormHorarioErr("Ruta, fecha y hora de salida son obligatorios.");
      return;
    }
    setFormHorarioSaving(true);
    try {
      await api.post("/api/horarios", {
        programacion_id:  programacionId,
        ruta_id:          Number(formHorario.ruta_id),
        fecha:            formHorario.fecha,
        hora_salida:      formHorario.hora_salida,
        turno:            formHorario.turno,
        duracion_est_min: Number(formHorario.duracion_est_min),
      });
      const params = new URLSearchParams();
      if (fecha)          params.set("fecha",           fecha);
      if (rutaId)         params.set("ruta_id",         rutaId);
      if (selectedProgId) params.set("programacion_id", selectedProgId);
      api.get(`/api/horarios?${params}`).then(d => setHorarios(d.horarios ?? []));
      setShowHorarioModal(false);
    } catch (err) {
      setFormHorarioErr(err.message || "No se pudo crear el horario.");
    } finally {
      setFormHorarioSaving(false);
    }
  };

  const handleEstadoProgram = async (estado) => {
    if (!programacionId) return;
    estado === "borrador" ? setSaving(true) : setApproving(true);
    setActionStatus(null);
    try {
      await api.patch(`/api/horarios/programacion/${programacionId}/estado?estado=${estado}`);
      setActionStatus({ ok: true, msg: `Programación marcada como "${estado}".` });
      setProgramaciones(prev =>
        prev.map(p => p.id === programacionId ? { ...p, estado } : p)
      );
    } catch (e) {
      setActionStatus({ ok: false, msg: e.message || "Error al actualizar el estado." });
    } finally {
      setSaving(false);
      setApproving(false);
      setTimeout(() => setActionStatus(null), 3500);
    }
  };

  const handleDuplicarSemana = async (e) => {
    e.preventDefault();
    setDupErr("");
    setDupResult(null);
    if (!dupForm.origen || !dupForm.destino) {
      setDupErr("Ambas fechas son obligatorias.");
      return;
    }
    setDuplicating(true);
    try {
      const body = {
        fecha_inicio_origen:  dupForm.origen,
        fecha_inicio_destino: dupForm.destino,
        incluir_asignaciones: true,
        omitir_existentes:    true,
      };
      if (rutaId) body.ruta_id = Number(rutaId);
      const res = await api.post("/api/horarios/duplicar-semana", body);
      setDupResult(res);
      setFecha(dupForm.destino);
    } catch (e) {
      setDupErr(e.message || "No se pudo duplicar la semana.");
    } finally {
      setDuplicating(false);
    }
  };

  const handleEliminarHorario = async (horarioId) => {
    if (!window.confirm("¿Eliminar este horario? Se perderán sus asignaciones. Esta acción no se puede deshacer.")) return;
    try {
      await api.delete(`/api/horarios/${horarioId}`);
      setHorarios(prev => prev.filter(h => h.id !== horarioId));
    } catch (err) {
      alert(err.message || "No se pudo eliminar el horario.");
    }
  };

  const handleQuitarAsignacion = async (asignacionId, horarioId) => {
    if (!window.confirm("¿Quitar la asignación de chofer de este horario?")) return;
    try {
      await api.delete(`/api/horarios/asignaciones/${asignacionId}`);
      setHorarios(prev => prev.map(h =>
        h.id === horarioId ? { ...h, chofer: null, asignacion_id: null, bus_placa: null } : h
      ));
    } catch (err) {
      alert(err.message || "No se pudo quitar la asignación.");
    }
  };

  const handleResolver = (conflictoId, horarioId, conflicto) => {
    setResolverModal({
      conflictoId, horarioId,
      tipo: conflicto.tipo,
      descripcion: conflicto.descripcion,
      severidad: conflicto.severidad,
      sugerencia: GUIA_POR_TIPO[conflicto.tipo] || null,
      esIA: false,
      cargandoIA: false,
    });
  };

  const pedirSugerenciaIA = async () => {
    setResolverModal(m => ({ ...m, cargandoIA: true }));
    try {
      const data = await api.post("/api/ia/chat", {
        intent: "resolver_conflicto",
        pregunta: "¿Cómo resuelvo este conflicto?",
        params: {
          tipo: resolverModal.tipo,
          descripcion: resolverModal.descripcion,
          severidad: resolverModal.severidad,
        },
      });
      if (data.respuesta) {
        setResolverModal(m => ({ ...m, sugerencia: data.respuesta, esIA: true, cargandoIA: false }));
      }
    } catch {
      setResolverModal(m => ({ ...m, cargandoIA: false }));
    }
  };

  const confirmarResolucion = async () => {
    const { conflictoId, horarioId } = resolverModal;
    setResolving(conflictoId);
    try {
      await api.patch(`/api/conflictos/${conflictoId}/resolver`);
      setHorarios(prev =>
        prev.map(h => h.id === horarioId ? { ...h, conflicto: null } : h)
      );
      setResolverModal(null);
    } catch {
      alert("No se pudo resolver. Verifica que tengas rol de Administrador ATU.");
    } finally {
      setResolving(null);
    }
  };

  const handleCrearProg = async (e) => {
    e.preventDefault();
    setFormErr("");
    if (!formProg.nombre.trim() || !formProg.fecha_inicio || !formProg.fecha_fin) {
      setFormErr("Nombre, fecha de inicio y fecha fin son obligatorios.");
      return;
    }
    setFormSaving(true);
    try {
      const nueva = await api.post("/api/programaciones", {
        nombre:       formProg.nombre.trim(),
        fecha_inicio: formProg.fecha_inicio,
        fecha_fin:    formProg.fecha_fin,
        observaciones: formProg.observaciones.trim() || null,
      });
      setProgramaciones(prev => [nueva, ...prev]);
      setSelectedProgId(String(nueva.id));
      setShowModal(false);
      setFormProg(emptyForm);
    } catch (e) {
      setFormErr(e.message || "No se pudo crear la programación.");
    } finally {
      setFormSaving(false);
    }
  };

  const conflictCount = horarios.filter(h => h.conflicto).length;
  const progActual = programaciones.find(p => p.id === programacionId);

  return (
    <div style={styles.layout}>
      <Sidebar active="grilla" onNav={onNav} onLogout={onLogout} user={user} />

      <main style={styles.main}>
        {/* Topbar */}
        <div style={styles.topbar}>
          <div>
            <div style={styles.breadcrumb}>Programación</div>
            <h1 style={styles.pageTitle}>Grilla de horarios</h1>
          </div>
          <div style={styles.badge}>
            {user?.role === "admin_atu" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>

        {/* Selector de programación */}
        <div style={styles.progBar}>
          <div style={styles.progBarLeft}>
            <label style={styles.progLabel}>Programación activa</label>
            <select
              value={selectedProgId}
              onChange={e => setSelectedProgId(e.target.value)}
              style={{ ...styles.select, minWidth: 280 }}
            >
              <option value="">— Selecciona una programación —</option>
              {programaciones.map(p => (
                <option key={p.id} value={p.id}>
                  {p.nombre} ({p.fecha_inicio} / {p.fecha_fin})
                </option>
              ))}
            </select>
            {progActual && (
              <span style={{ ...styles.estadoBadge, ...(ESTADO_BADGE[progActual.estado] ?? {}) }}>
                {progActual.estado}
              </span>
            )}
            {user?.role === "admin_atu" && progActual && ["borrador", "revision"].includes(progActual.estado) && (
              <button style={styles.btnDanger} onClick={handleEliminarProg}>
                Eliminar
              </button>
            )}
          </div>
          {user?.role === "admin_atu" && (
            <button style={styles.btnPrimary} onClick={() => setShowModal(true)}>
              + Nueva programación
            </button>
          )}
        </div>

        {/* Controles de filtro */}
        <div style={styles.controls}>
          <select value={rutaId} onChange={e => setRutaId(e.target.value)} style={styles.select}>
            <option value="">Todas las rutas</option>
            {rutas.map(r => (
              <option key={r.id} value={r.id}>{r.codigo} — {r.nombre}</option>
            ))}
          </select>
          <input
            type="date" value={fecha}
            onChange={e => setFecha(e.target.value)}
            min={progActual?.fecha_inicio}
            max={progActual?.fecha_fin}
            style={styles.select}
          />
          <button
            style={{ ...styles.btnSecondary, opacity: (!programacionId || saving || horarios.length === 0) ? 0.5 : 1 }}
            onClick={() => handleEstadoProgram("borrador")}
            disabled={!programacionId || saving || horarios.length === 0}
            title={horarios.length === 0 ? "No hay horarios en esta semana para guardar" : ""}
          >
            {saving ? "Guardando…" : "Guardar borrador"}
          </button>
          {user?.role === "admin_atu" && (
            <button
              style={{ ...styles.btnSecondary, opacity: duplicating ? 0.5 : 1 }}
              onClick={() => { setShowDupModal(true); setDupErr(""); setDupResult(null); setDupForm({ origen: fecha, destino: "" }); }}
              disabled={duplicating}
            >
              {duplicating ? "Duplicando…" : "Duplicar semana"}
            </button>
          )}
          {user?.role === "admin_atu" && (
            <button
              style={{ ...styles.btnPrimary, opacity: (!programacionId || approving || horarios.length === 0) ? 0.5 : 1 }}
              onClick={() => handleEstadoProgram("aprobada")}
              disabled={!programacionId || approving || horarios.length === 0}
              title={horarios.length === 0 ? "No hay horarios en esta semana para aprobar" : ""}
            >
              {approving ? "Aprobando…" : "Aprobar programación"}
            </button>
          )}
          {user?.role === "admin_atu" && programacionId && (
            <button
              style={styles.btnPrimary}
              onClick={() => {
                setFormHorarioErr("");
                setFormHorario({ ruta_id: rutaId || "", fecha, hora_salida: "", turno: "manana", duracion_est_min: 60 });
                setShowHorarioModal(true);
              }}
            >
              + Agregar horario
            </button>
          )}
          {conflictCount > 0 && (
            <span style={styles.conflictBadge}>
              {conflictCount} conflicto{conflictCount > 1 ? "s" : ""}
            </span>
          )}
          {actionStatus && (
            <span style={actionStatus.ok ? styles.actionOk : styles.actionErr}>
              {actionStatus.msg}
            </span>
          )}
        </div>

        {/* Tabla */}
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                {["Hora salida", "Ruta", "Chofer", "Turno", "Duración", "Estado"].map(h => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={6} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                    Cargando…
                  </td>
                </tr>
              )}
              {!loading && horarios.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...styles.td, textAlign: "center", color: "#aaa" }}>
                    {selectedProgId
                      ? "Sin horarios para esta programación / ruta / fecha."
                      : "Selecciona una programación para ver sus horarios."}
                  </td>
                </tr>
              )}
              {!loading && horarios.map(h => {
                const tieneConflicto = !!h.conflicto;
                return (
                  <tr key={h.id} style={tieneConflicto ? styles.rowConflicto : {}}>
                    <td style={styles.td}>
                      <strong style={{ fontFamily: "'Space Mono',monospace", fontSize: 13 }}>
                        {h.hora_salida}
                      </strong>
                    </td>
                    <td style={styles.td}>
                      {rutas.find(r => r.id === h.ruta_id)?.codigo ?? `Ruta #${h.ruta_id}`}
                    </td>
                    <td style={styles.td}>
                      {h.chofer
                        ? (
                          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                            <div style={styles.choferBadge}>
                              <span style={styles.avatar}>
                                {h.chofer.nombre.split(" ").map(w => w[0]).slice(0, 2).join("")}
                              </span>
                              <span>{h.chofer.nombre}</span>
                            </div>
                            {(user?.role === "admin_atu" || user?.role === "supervisor_area") && h.asignacion_id && (
                              <button
                                style={styles.removeBtn}
                                onClick={() => handleQuitarAsignacion(h.asignacion_id, h.id)}
                              >
                                Quitar
                              </button>
                            )}
                            {(user?.role === "admin_atu" || user?.role === "supervisor_area") && h.asignacion_id && onSugerirReemplazo && (
                              <button
                                style={styles.assignBtn}
                                onClick={() => onSugerirReemplazo(h.asignacion_id)}
                              >
                                Reemplazar
                              </button>
                            )}
                          </div>
                        )
                        : (
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ color: "#bbb", fontSize: 12 }}>Sin asignar</span>
                            {(user?.role === "admin_atu" || user?.role === "supervisor_area") && (
                              <button
                                style={styles.assignBtn}
                                onClick={() => abrirAsignar(h)}
                              >
                                Asignar
                              </button>
                            )}
                          </div>
                        )
                      }
                    </td>
                    <td style={styles.td}>
                      <span style={{ ...styles.tag, ...(TURNO_STYLE[h.turno] ?? {}) }}>
                        {TURNO_LABEL[h.turno] ?? h.turno}
                      </span>
                    </td>
                    <td style={styles.td}>{h.duracion_est_min} min</td>
                    <td style={styles.td}>
                      {tieneConflicto ? (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                            <span style={{ ...styles.tag, ...(SEV_STYLE[h.conflicto.severidad] ?? SEV_STYLE.media) }}>
                              Conflicto
                            </span>
                            <span style={{ fontSize: 11, color: "#9B2C2C" }}>
                              {h.conflicto.tipo.replace(/_/g, " ")}
                            </span>
                          </div>
                          <div style={styles.conflictDesc}>{h.conflicto.descripcion}</div>
                          {user?.role === "admin_atu" && (
                            <button
                              style={styles.resolveBtn}
                                onClick={() => handleResolver(h.conflicto.id, h.id, h.conflicto)}
                            >
                              Resolver
                            </button>
                          )}
                        </div>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5, alignItems: "flex-start" }}>
                          <span style={{
                            ...styles.tag,
                            background: !h.chofer ? "#f0f0f0" : h.activo ? "#EAF3DE" : "#e0e0e0",
                            color:      !h.chofer ? "#999"    : h.activo ? "#27500A" : "#666",
                          }}>
                            {!h.chofer ? "Sin cubrir" : h.activo ? "Activo" : "Inactivo"}
                          </span>
                          {user?.role === "admin_atu" && (
                            <button
                              style={styles.deleteBtn}
                              onClick={() => handleEliminarHorario(h.id)}
                            >
                              Eliminar horario
                            </button>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {!loading && horarios.length > 0 && (
          <div style={styles.successBanner}>
            {horarios.length} horario{horarios.length > 1 ? "s" : ""} para {fecha}.{" "}
            {conflictCount > 0
              ? `${conflictCount} con conflicto activo.`
              : "Sin conflictos."}
          </div>
        )}
      </main>

      {/* Modal duplicar semana */}
      {showDupModal && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Duplicar semana</h2>
              <button style={styles.modalClose} onClick={() => setShowDupModal(false)}>×</button>
            </div>
            <form onSubmit={handleDuplicarSemana} style={styles.form}>
              <label style={styles.label}>Semana origen (lunes de la semana a copiar)</label>
              <input
                type="date" style={styles.input}
                value={dupForm.origen}
                onChange={e => setDupForm(f => ({ ...f, origen: e.target.value }))}
              />
              <label style={styles.label}>Semana destino (lunes de la semana nueva)</label>
              <input
                type="date" style={styles.input}
                value={dupForm.destino}
                onChange={e => setDupForm(f => ({ ...f, destino: e.target.value }))}
              />
              {dupErr && <div style={styles.actionErr}>{dupErr}</div>}
              {dupResult && (
                <div style={styles.actionOk}>
                  Duplicado: {dupResult.horarios_duplicados} horarios,{" "}
                  {dupResult.asignaciones_duplicadas} asignaciones.
                  {dupResult.advertencias?.length > 0 && ` (${dupResult.advertencias.length} advertencias)`}
                </div>
              )}
              <div style={styles.formActions}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => setShowDupModal(false)}>
                  Cerrar
                </button>
                {!dupResult && (
                  <button type="submit" style={{ ...styles.btnPrimary, opacity: duplicating ? 0.6 : 1 }}
                    disabled={duplicating}>
                    {duplicating ? "Duplicando…" : "Duplicar"}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal asignar chofer (admin o supervisor de área) */}
      {asigTarget && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Asignar chofer</h2>
              <button style={styles.modalClose} onClick={() => setAsigTarget(null)}>×</button>
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#888", marginBottom: 16 }}>
              Horario {asigTarget.hora_salida} · {rutas.find(r => r.id === asigTarget.ruta_id)?.codigo ?? `Ruta #${asigTarget.ruta_id}`} · {asigTarget.fecha}
            </div>
            <form onSubmit={handleCrearAsignacion} style={styles.form}>
              <label style={styles.label}>Chofer *</label>
              <select
                style={styles.input}
                value={formAsig.chofer_id}
                onChange={e => setFormAsig(f => ({ ...f, chofer_id: e.target.value }))}
              >
                <option value="">— Selecciona un chofer —</option>
                {asigChoferes.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.nombres} {c.apellidos} — Lic. {c.numero_licencia}
                  </option>
                ))}
              </select>
              <label style={styles.label}>Área *</label>
              <select
                style={styles.input}
                value={formAsig.area_id}
                onChange={e => setFormAsig(f => ({ ...f, area_id: e.target.value }))}
                disabled={user?.role === "supervisor_area"}
              >
                <option value="">— Selecciona un área —</option>
                {asigConcs.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
              <label style={styles.label}>Bus (opcional)</label>
              <select
                style={styles.input}
                value={formAsig.bus_placa}
                onChange={e => setFormAsig(f => ({ ...f, bus_placa: e.target.value }))}
              >
                <option value="">— Sin bus asignado —</option>
                {asigBuses.map(b => (
                  <option key={b.placa} value={b.placa}>{b.placa} — {b.tipo}</option>
                ))}
              </select>
              <label style={styles.label}>Notas (opcional)</label>
              <input
                style={styles.input}
                placeholder="Observaciones de la asignación"
                value={formAsig.notas}
                onChange={e => setFormAsig(f => ({ ...f, notas: e.target.value }))}
              />
              {formAsigErr && <div style={styles.formErr}>{formAsigErr}</div>}
              <div style={styles.formActions}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => setAsigTarget(null)}>
                  Cancelar
                </button>
                <button type="submit"
                  style={{ ...styles.btnPrimary, opacity: formAsigSaving ? 0.6 : 1 }}
                  disabled={formAsigSaving}>
                  {formAsigSaving ? "Asignando…" : "Confirmar asignación"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal agregar horario (admin only) */}
      {showHorarioModal && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Agregar horario</h2>
              <button style={styles.modalClose} onClick={() => setShowHorarioModal(false)}>×</button>
            </div>
            <form onSubmit={handleCrearHorario} style={styles.form}>
              <label style={styles.label}>Ruta *</label>
              <select
                style={styles.input}
                value={formHorario.ruta_id}
                onChange={e => setFormHorario(f => ({ ...f, ruta_id: e.target.value }))}
              >
                <option value="">— Selecciona una ruta —</option>
                {rutas.map(r => (
                  <option key={r.id} value={r.id}>{r.codigo} — {r.nombre}</option>
                ))}
              </select>
              <div style={{ display: "flex", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Fecha *</label>
                  <input
                    type="date" style={styles.input}
                    value={formHorario.fecha}
                    min={progActual?.fecha_inicio}
                    max={progActual?.fecha_fin}
                    onChange={e => setFormHorario(f => ({ ...f, fecha: e.target.value }))}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Hora salida *</label>
                  <input
                    type="time" style={styles.input}
                    value={formHorario.hora_salida}
                    onChange={e => setFormHorario(f => ({ ...f, hora_salida: e.target.value }))}
                  />
                </div>
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Turno *</label>
                  <select
                    style={styles.input}
                    value={formHorario.turno}
                    onChange={e => setFormHorario(f => ({ ...f, turno: e.target.value }))}
                  >
                    <option value="manana">Mañana</option>
                    <option value="tarde">Tarde</option>
                    <option value="noche">Noche</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Duración estimada (min) *</label>
                  <input
                    type="number" style={styles.input}
                    min={15} max={240}
                    value={formHorario.duracion_est_min}
                    onChange={e => setFormHorario(f => ({ ...f, duracion_est_min: e.target.value }))}
                  />
                </div>
              </div>
              {formHorarioErr && <div style={styles.formErr}>{formHorarioErr}</div>}
              <div style={styles.formActions}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => setShowHorarioModal(false)}>
                  Cancelar
                </button>
                <button type="submit"
                  style={{ ...styles.btnPrimary, opacity: formHorarioSaving ? 0.6 : 1 }}
                  disabled={formHorarioSaving}>
                  {formHorarioSaving ? "Creando…" : "Agregar horario"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal nueva programación */}
      {showModal && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Nueva programación</h2>
              <button style={styles.modalClose} onClick={() => { setShowModal(false); setFormErr(""); setFormProg(emptyForm); }}>
                ×
              </button>
            </div>
            <form onSubmit={handleCrearProg} style={styles.form}>
              <label style={styles.label}>Nombre *</label>
              <input
                style={styles.input}
                placeholder="Ej. Programación Semana 23"
                value={formProg.nombre}
                onChange={e => setFormProg(p => ({ ...p, nombre: e.target.value }))}
              />
              <div style={{ display: "flex", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Fecha inicio *</label>
                  <input
                    type="date" style={styles.input}
                    value={formProg.fecha_inicio}
                    onChange={e => setFormProg(p => ({ ...p, fecha_inicio: e.target.value }))}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Fecha fin *</label>
                  <input
                    type="date" style={styles.input}
                    value={formProg.fecha_fin}
                    onChange={e => setFormProg(p => ({ ...p, fecha_fin: e.target.value }))}
                  />
                </div>
              </div>
              <label style={styles.label}>Observaciones</label>
              <textarea
                style={{ ...styles.input, height: 72, resize: "vertical" }}
                placeholder="Opcional"
                value={formProg.observaciones}
                onChange={e => setFormProg(p => ({ ...p, observaciones: e.target.value }))}
              />
              {formErr && <div style={styles.formErr}>{formErr}</div>}
              <div style={styles.formActions}>
                <button type="button" style={styles.btnSecondary}
                  onClick={() => { setShowModal(false); setFormErr(""); setFormProg(emptyForm); }}>
                  Cancelar
                </button>
                <button type="submit" style={{ ...styles.btnPrimary, opacity: formSaving ? 0.6 : 1 }}
                  disabled={formSaving}>
                  {formSaving ? "Creando…" : "Crear programación"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal resolver conflicto con sugerencia IA */}
      {resolverModal && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Resolver conflicto</h2>
              <button style={styles.modalClose} onClick={() => setResolverModal(null)}>×</button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                <span style={{ ...styles.tag, ...(SEV_STYLE[resolverModal.severidad] ?? SEV_STYLE.media) }}>
                  {resolverModal.tipo.replace(/_/g, " ")}
                </span>
                <span style={{ ...styles.tag, ...(SEV_STYLE[resolverModal.severidad] ?? SEV_STYLE.media) }}>
                  {resolverModal.severidad}
                </span>
              </div>
              <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#374151", margin: 0, lineHeight: 1.5 }}>
                {resolverModal.descripcion}
              </p>
              {resolverModal.sugerencia && (
                <div style={{
                  background: resolverModal.esIA ? "#EFF6FF" : "#F0FDF4",
                  border: `1px solid ${resolverModal.esIA ? "#BFDBFE" : "#BBF7D0"}`,
                  borderRadius: 8, padding: "12px 14px",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 700, color: resolverModal.esIA ? "#1D4ED8" : "#15803D" }}>
                      {resolverModal.esIA ? "Sugerencia del Copiloto IA" : "Guía de resolución"}
                    </span>
                    {!resolverModal.esIA && (
                      <button
                        onClick={pedirSugerenciaIA}
                        disabled={resolverModal.cargandoIA}
                        style={{ fontSize: 10, padding: "2px 8px", borderRadius: 5, border: "1px solid #BFDBFE", background: "#EFF6FF", color: "#1D4ED8", cursor: "pointer", fontFamily: "inherit" }}
                      >
                        {resolverModal.cargandoIA ? "Consultando…" : "✨ Pedir análisis IA"}
                      </button>
                    )}
                  </div>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: resolverModal.esIA ? "#1E3A5F" : "#1A3D2B", lineHeight: 1.6 }}>
                    {resolverModal.sugerencia}
                  </div>
                </div>
              )}
              <div style={styles.formActions}>
                <button style={styles.btnSecondary} onClick={() => setResolverModal(null)}>
                  Cancelar
                </button>
                <button
                  style={{ ...styles.btnPrimary, opacity: resolving === resolverModal.conflictoId ? 0.6 : 1 }}
                  disabled={resolving === resolverModal.conflictoId}
                  onClick={confirmarResolucion}
                >
                  {resolving === resolverModal.conflictoId ? "Resolviendo…" : "Confirmar resolución"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  layout:    { display: "flex", minHeight: "100vh", background: "#f4f6f8" },
  main:      { flex: 1, padding: 28, display: "flex", flexDirection: "column", gap: 18, overflow: "auto" },
  topbar:    { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  breadcrumb:{ fontFamily: "'DM Sans',sans-serif", fontSize: 11, color: "#888", marginBottom: 3 },
  pageTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 22, fontWeight: 600, color: "#111" },
  badge: {
    background: "#185FA5", color: "#E6F1FB",
    fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500,
    padding: "5px 12px", borderRadius: 20,
  },
  progBar: {
    display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap",
    gap: 10, background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10,
    padding: "12px 16px",
  },
  progBarLeft: { display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" },
  progLabel: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 500, color: "#888",
    whiteSpace: "nowrap",
  },
  estadoBadge: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500,
    padding: "3px 10px", borderRadius: 20,
  },
  controls: { display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" },
  select: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "8px 12px",
    borderRadius: 8, border: "1px solid #ddd", background: "#fff", color: "#222", outline: "none",
  },
  btnSecondary: {
    padding: "8px 16px", borderRadius: 8, border: "1px solid #ddd", background: "#fff",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#444", cursor: "pointer",
  },
  btnPrimary: {
    padding: "8px 18px", borderRadius: 8, border: "none", background: "#185FA5",
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 500, color: "#E6F1FB", cursor: "pointer",
  },
  conflictBadge: {
    background: "#FCEBEB", color: "#791F1F", border: "1px solid #F7C1C1",
    fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 600,
    padding: "4px 12px", borderRadius: 20,
  },
  tableWrap: { background: "#fff", border: "0.5px solid #e8e8e8", borderRadius: 10, overflow: "hidden" },
  table:     { width: "100%", borderCollapse: "collapse" },
  th: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 11, fontWeight: 500, color: "#888",
    padding: "10px 14px", borderBottom: "1px solid #f0f0f0", textAlign: "left",
    background: "#fafafa", textTransform: "uppercase", letterSpacing: "0.4px",
  },
  td: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#222",
    padding: "11px 14px", borderBottom: "0.5px solid #f4f4f4", verticalAlign: "top",
  },
  rowConflicto: { background: "#fff9f9" },
  choferBadge:  { display: "inline-flex", alignItems: "center", gap: 7 },
  avatar: {
    width: 24, height: 24, borderRadius: "50%", background: "#B5D4F4",
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    fontSize: 10, fontWeight: 600, color: "#0C447C", flexShrink: 0,
  },
  tag:         { display: "inline-block", padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500 },
  conflictDesc:{ fontSize: 11, color: "#9B2C2C", lineHeight: 1.4, maxWidth: 340 },
  resolveBtn: {
    padding: "3px 10px", borderRadius: 6, border: "1px solid #F7C1C1",
    background: "#FCEBEB", color: "#791F1F", fontSize: 11,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif", width: "fit-content",
  },
  assignBtn: {
    padding: "3px 10px", borderRadius: 6, border: "1px solid #B5D4F4",
    background: "#E6F1FB", color: "#0C447C", fontSize: 11,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif", width: "fit-content",
  },
  removeBtn: {
    padding: "3px 10px", borderRadius: 6, border: "1px solid #F0D1A0",
    background: "#FAEEDA", color: "#633806", fontSize: 11,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif", width: "fit-content",
  },
  deleteBtn: {
    padding: "3px 9px", borderRadius: 6, border: "1px solid #e0e0e0",
    background: "transparent", color: "#bbb", fontSize: 10,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif", width: "fit-content",
  },
  btnDanger: {
    padding: "4px 12px", borderRadius: 6, border: "1px solid #F7C1C1",
    background: "#FCEBEB", color: "#791F1F", fontSize: 12, fontWeight: 500,
    cursor: "pointer", fontFamily: "'DM Sans',sans-serif",
  },
  successBanner: {
    background: "#EAF3DE", border: "0.5px solid #C0DD97", borderRadius: 8,
    padding: "11px 16px", fontFamily: "'DM Sans',sans-serif", fontSize: 13, color: "#27500A",
  },
  actionOk: {
    background: "#EAF3DE", border: "1px solid #C0DD97", borderRadius: 6,
    padding: "5px 12px", fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#27500A",
  },
  actionErr: {
    background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6,
    padding: "5px 12px", fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#791F1F",
  },
  // Modal
  overlay: {
    position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
  },
  modal: {
    background: "#fff", borderRadius: 14, padding: 28, width: 480, maxWidth: "95vw",
    boxShadow: "0 8px 40px rgba(0,0,0,0.18)",
  },
  modalHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 },
  modalTitle:  { fontFamily: "'DM Sans',sans-serif", fontSize: 17, fontWeight: 600, color: "#111", margin: 0 },
  modalClose: {
    background: "none", border: "none", fontSize: 22, cursor: "pointer", color: "#888",
    lineHeight: 1, padding: "0 4px",
  },
  form:    { display: "flex", flexDirection: "column", gap: 12 },
  label:   { fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 500, color: "#555" },
  input: {
    fontFamily: "'DM Sans',sans-serif", fontSize: 13, padding: "9px 12px",
    borderRadius: 8, border: "1px solid #ddd", outline: "none", width: "100%",
    boxSizing: "border-box", color: "#222",
  },
  formErr: {
    background: "#FCEBEB", border: "1px solid #F7C1C1", borderRadius: 6,
    padding: "8px 12px", fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#791F1F",
  },
  formActions: { display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 4 },
};
