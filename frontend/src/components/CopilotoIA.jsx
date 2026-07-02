import { useState, useCallback, useEffect } from "react";
import { api } from "../api";

const COLORES_SEVERIDAD = {
  alta:  { fondo: "#FEE2E2", borde: "#EF4444", texto: "#991B1B" },
  media: { fondo: "#FEF9C3", borde: "#EAB308", texto: "#713F12" },
  baja:  { fondo: "#DCFCE7", borde: "#22C55E", texto: "#14532D" },
};

const INTENTS = [
  { id: "disponibilidad",      label: "¿Quién está disponible?",         placeholder: "Ej: ¿Quién está libre el viernes tarde?" },
  { id: "explicar_alerta",     label: "Explicar alerta de chofer",        placeholder: "Ej: ¿Por qué hay alerta para el chofer 5?" },
  { id: "horas_area",          label: "Horas trabajadas por área",        placeholder: "Ej: ¿Cuántas horas trabajó el área norte esta semana?" },
  { id: "estado_programacion", label: "Estado de una programación",       placeholder: "Ej: ¿Cómo está la programación 3?" },
];

const PARAMS_POR_INTENT = {
  disponibilidad:      [{ key: "fecha",            label: "Fecha (AAAA-MM-DD)" }, { key: "turno", label: "Turno (manana/tarde/noche)" }],
  explicar_alerta:     [{ key: "chofer_id",         label: "ID del chofer" }],
  horas_area:          [{ key: "area_id",           label: "ID del área" }, { key: "fecha", label: "Fecha de referencia (AAAA-MM-DD)" }],
  estado_programacion: [{ key: "programacion_id",   label: "ID de la programación" }],
};

export default function CopilotoIA({ user, onNavToGrilla, reemplazoTrigger }) {
  const [abierto,         setAbierto]         = useState(false);
  const [tab,             setTab]             = useState("fatiga");
  const [cargandoFatiga,  setCargandoFatiga]  = useState(false);
  const [cargandoReemplazo, setCargandoReemplazo] = useState(false);
  const [cargandoChat,    setCargandoChat]    = useState(false);
  const [error,           setError]           = useState("");

  // Tab Alertas de Fatiga
  const [alertas,    setAlertas]    = useState(null);

  // Tab Sugerir Reemplazo
  const [asigId,     setAsigId]     = useState("");
  const [reemplazo,  setReemplazo]  = useState(null);

  // Tab Asistente Chat
  const [intentSel,  setIntentSel]  = useState(INTENTS[0].id);
  const [params,     setParams]     = useState({});
  const [pregunta,   setPregunta]   = useState("");
  const [respuesta,  setRespuesta]  = useState("");

  useEffect(() => {
    if (!reemplazoTrigger) return;
    const { asigId: id } = reemplazoTrigger;
    setAbierto(true);
    setTab("reemplazo");
    setAsigId(String(id));
    setReemplazo(null);
    setError("");
    setCargandoReemplazo(true);
    api.post(`/api/ia/sugerir-reemplazo/${id}`)
      .then(data => setReemplazo(data))
      .catch(e => setError(e.message))
      .finally(() => setCargandoReemplazo(false));
  }, [reemplazoTrigger]);

  const roles_permitidos = ["admin_atu", "supervisor_area"];
  if (!user || !roles_permitidos.includes(user.role)) return null;

  const limpiarError = () => setError("");

  const cargarAlertas = useCallback(async () => {
    setCargandoFatiga(true); limpiarError();
    try {
      const data = await api.get("/api/ia/alertas-fatiga");
      setAlertas(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargandoFatiga(false);
    }
  }, []);

  const onTabChange = (t) => {
    setTab(t);
    limpiarError();
    if (t === "fatiga" && alertas === null) cargarAlertas();
  };

  const pedirReemplazo = async () => {
    if (!asigId.trim()) { setError("Ingresa el ID de la asignación"); return; }
    setCargandoReemplazo(true); limpiarError(); setReemplazo(null);
    try {
      const data = await api.post(`/api/ia/sugerir-reemplazo/${asigId.trim()}`);
      setReemplazo(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargandoReemplazo(false);
    }
  };

  const enviarChat = async () => {
    if (!pregunta.trim()) { setError("Escribe una pregunta"); return; }
    setCargandoChat(true); limpiarError(); setRespuesta("");
    try {
      const data = await api.post("/api/ia/chat", {
        intent: intentSel,
        pregunta: pregunta.trim(),
        params,
      });
      setRespuesta(data.respuesta);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargandoChat(false);
    }
  };

  const intentActual = INTENTS.find(i => i.id === intentSel);

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => { setAbierto(a => !a); if (!abierto && tab === "fatiga" && alertas === null) cargarAlertas(); }}
        title="Copiloto IA"
        style={{
          position: "fixed", bottom: 28, right: 28, zIndex: 1000,
          width: 56, height: 56, borderRadius: "50%",
          background: "linear-gradient(135deg, #1E40AF, #3B82F6)",
          border: "none", cursor: "pointer", boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 26, transition: "transform 0.2s",
        }}
        onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
        onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
      >
        🤖
      </button>

      {/* Panel */}
      {abierto && (
        <div style={{
          position: "fixed", bottom: 96, right: 28, zIndex: 999,
          width: 400, maxHeight: "75vh",
          background: "#fff", borderRadius: 14,
          boxShadow: "0 8px 32px rgba(0,0,0,0.22)",
          display: "flex", flexDirection: "column",
          fontFamily: "'DM Sans', sans-serif", overflow: "hidden",
        }}>
          {/* Header */}
          <div style={{
            background: "linear-gradient(135deg, #042C53, #1E40AF)",
            padding: "14px 18px", display: "flex", alignItems: "center",
            justifyContent: "space-between",
          }}>
            <div>
              <div style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>🤖 Copiloto IA</div>
              <div style={{ color: "#93C5FD", fontSize: 12 }}>Asistente de programación MetroHub</div>
            </div>
            <button
              onClick={() => setAbierto(false)}
              style={{ background: "none", border: "none", color: "#93C5FD", cursor: "pointer", fontSize: 20 }}
            >✕</button>
          </div>

          {/* Tabs */}
          <div style={{ display: "flex", borderBottom: "1px solid #E5E7EB" }}>
            {[
              { id: "fatiga",    label: "⚠️ Fatiga"    },
              { id: "reemplazo", label: "🔄 Reemplazo" },
              { id: "chat",      label: "💬 Asistente" },
            ].map(t => (
              <button
                key={t.id}
                onClick={() => onTabChange(t.id)}
                style={{
                  flex: 1, padding: "10px 4px", border: "none", cursor: "pointer",
                  fontSize: 12, fontWeight: tab === t.id ? 700 : 400,
                  background: tab === t.id ? "#EFF6FF" : "#fff",
                  borderBottom: tab === t.id ? "2px solid #3B82F6" : "2px solid transparent",
                  color: tab === t.id ? "#1D4ED8" : "#6B7280",
                  transition: "all 0.15s",
                }}
              >{t.label}</button>
            ))}
          </div>

          {/* Contenido */}
          <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
            {error && (
              <div style={{
                background: "#FEE2E2", color: "#991B1B", borderRadius: 8,
                padding: "10px 12px", marginBottom: 12, fontSize: 13,
              }}>
                ⚠️ {error}
              </div>
            )}

            {/* ── Tab: Alertas de Fatiga ── */}
            {tab === "fatiga" && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div>
                    <span style={{ fontSize: 13, color: "#374151", fontWeight: 600 }}>Alertas de esta semana</span>
                    {alertas?.actualizado_en && !cargandoFatiga && (
                      <div style={{ fontSize: 10, color: "#9CA3AF", marginTop: 1 }}>
                        hace {Math.round((Date.now() / 1000 - alertas.actualizado_en) / 60)} min · caché 5 min
                      </div>
                    )}
                  </div>
                  <button onClick={cargarAlertas} style={estiloBotonSecundario}>
                    {cargandoFatiga ? "Cargando…" : "↻ Actualizar"}
                  </button>
                </div>
                {cargandoFatiga && <div style={estiloCargando}>Analizando programación…</div>}
                {!cargandoFatiga && alertas && alertas.total === 0 && (
                  <div style={{ textAlign: "center", color: "#6B7280", fontSize: 13, padding: 20 }}>
                    ✅ Sin alertas detectadas esta semana
                  </div>
                )}
                {!cargandoFatiga && alertas?.alertas?.map((a, i) => {
                  const c = COLORES_SEVERIDAD[a.severidad] || COLORES_SEVERIDAD.baja;
                  return (
                    <div key={i} style={{
                      background: c.fondo, border: `1px solid ${c.borde}`,
                      borderRadius: 8, padding: "10px 12px", marginBottom: 10,
                    }}>
                      <div style={{ fontWeight: 700, fontSize: 13, color: c.texto }}>
                        {a.nombres} {a.apellidos}
                        <span style={{
                          float: "right", fontSize: 10, background: c.borde,
                          color: "#fff", padding: "1px 6px", borderRadius: 10,
                        }}>{a.severidad.toUpperCase()}</span>
                      </div>
                      <div style={{ fontSize: 12, color: "#374151", marginTop: 4 }}>{a.alerta}</div>
                      <div style={{ fontSize: 11, color: "#6B7280", marginTop: 4 }}>
                        💡 {a.sugerencia}
                      </div>
                      {a.fecha_referencia && onNavToGrilla && (
                        <button
                          onClick={() => { setAbierto(false); onNavToGrilla(a.fecha_referencia); }}
                          style={{
                            marginTop: 8, padding: "3px 10px", borderRadius: 6,
                            border: `1px solid ${c.borde}`, background: "transparent",
                            color: c.texto, fontSize: 10, cursor: "pointer",
                            fontFamily: "inherit",
                          }}
                        >
                          Ver en Grilla →
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* ── Tab: Sugerir Reemplazo ── */}
            {tab === "reemplazo" && (
              <div>
                <p style={{ fontSize: 13, color: "#6B7280", marginBottom: 12 }}>
                  Ingresa el ID de la asignación que necesita cobertura y la IA sugerirá el mejor reemplazo disponible.
                </p>
                <label style={estiloLabel}>ID de asignación</label>
                <input
                  type="number"
                  value={asigId}
                  onChange={e => setAsigId(e.target.value)}
                  placeholder="Ej: 42"
                  style={estiloInput}
                  onKeyDown={e => e.key === "Enter" && pedirReemplazo()}
                />
                <button
                  onClick={pedirReemplazo}
                  disabled={cargandoReemplazo}
                  style={{ ...estiloBotonPrincipal, marginTop: 8, width: "100%" }}
                >
                  {cargandoReemplazo ? "Consultando IA…" : "🔍 Sugerir reemplazo"}
                </button>

                {reemplazo && (
                  <div style={{ marginTop: 14 }}>
                    <div style={{ fontSize: 12, color: "#374151", marginBottom: 6, fontWeight: 600 }}>
                      Turno: {reemplazo.horario?.turno} — {reemplazo.horario?.fecha} — {reemplazo.horario?.ruta_nombre}
                    </div>
                    <div style={{
                      background: "#EFF6FF", border: "1px solid #BFDBFE",
                      borderRadius: 8, padding: "10px 12px",
                    }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#1D4ED8", marginBottom: 4 }}>
                        Recomendación IA ({reemplazo.candidatos_evaluados} candidatos evaluados)
                      </div>
                      <div style={{ fontSize: 12, color: "#1E3A5F", lineHeight: 1.5 }}>
                        {reemplazo.recomendacion_ia?.recomendacion}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Tab: Asistente Chat ── */}
            {tab === "chat" && (
              <div>
                <label style={estiloLabel}>¿Sobre qué quieres preguntar?</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 12 }}>
                  {INTENTS.map(i => (
                    <button
                      key={i.id}
                      onClick={() => { setIntentSel(i.id); setParams({}); setRespuesta(""); }}
                      style={{
                        padding: "7px 8px", borderRadius: 8, border: "1px solid",
                        fontSize: 11, cursor: "pointer", textAlign: "left",
                        borderColor: intentSel === i.id ? "#3B82F6" : "#D1D5DB",
                        background: intentSel === i.id ? "#EFF6FF" : "#F9FAFB",
                        color: intentSel === i.id ? "#1D4ED8" : "#374151",
                        fontWeight: intentSel === i.id ? 700 : 400,
                      }}
                    >{i.label}</button>
                  ))}
                </div>

                {PARAMS_POR_INTENT[intentSel]?.map(p => (
                  <div key={p.key} style={{ marginBottom: 8 }}>
                    <label style={estiloLabel}>{p.label}</label>
                    <input
                      value={params[p.key] || ""}
                      onChange={e => setParams(prev => ({ ...prev, [p.key]: e.target.value }))}
                      style={estiloInput}
                    />
                  </div>
                ))}

                <label style={estiloLabel}>Tu pregunta</label>
                <textarea
                  value={pregunta}
                  onChange={e => setPregunta(e.target.value)}
                  placeholder={intentActual?.placeholder}
                  rows={3}
                  style={{ ...estiloInput, resize: "vertical", fontFamily: "inherit" }}
                />
                <button
                  onClick={enviarChat}
                  disabled={cargandoChat}
                  style={{ ...estiloBotonPrincipal, marginTop: 8, width: "100%" }}
                >
                  {cargandoChat ? "Consultando IA…" : "✉️ Preguntar"}
                </button>

                {respuesta && (
                  <div style={{
                    marginTop: 12, background: "#F0FDF4", border: "1px solid #BBF7D0",
                    borderRadius: 8, padding: "10px 12px",
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#15803D", marginBottom: 4 }}>
                      Respuesta del Copiloto IA
                    </div>
                    <div style={{ fontSize: 12, color: "#1A3D2B", lineHeight: 1.6 }}>{respuesta}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

const estiloLabel = {
  display: "block", fontSize: 11, fontWeight: 600,
  color: "#374151", marginBottom: 4,
};

const estiloInput = {
  width: "100%", padding: "8px 10px", borderRadius: 8,
  border: "1px solid #D1D5DB", fontSize: 13, boxSizing: "border-box",
  outline: "none",
};

const estiloBotonPrincipal = {
  background: "linear-gradient(135deg, #1D4ED8, #3B82F6)",
  color: "#fff", border: "none", borderRadius: 8,
  padding: "9px 14px", cursor: "pointer", fontSize: 13, fontWeight: 600,
};

const estiloBotonSecundario = {
  background: "#F3F4F6", color: "#374151", border: "1px solid #D1D5DB",
  borderRadius: 6, padding: "5px 10px", cursor: "pointer", fontSize: 12,
};

const estiloCargando = {
  textAlign: "center", color: "#6B7280", fontSize: 13, padding: "20px 0",
};
