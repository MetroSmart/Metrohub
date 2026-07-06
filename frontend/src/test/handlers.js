import { http, HttpResponse } from "msw";

const API = "http://localhost:8000";

// ── Datos seed reutilizables por los tests ─────────────────────────
export const mockKpis = {
  fecha: "2026-06-11",
  rutas_activas: 3,
  choferes_activos: 12,
  buses_operativos: 8,
  asignaciones_hoy: 5,
  conflictos_abiertos: 1,
  certif_por_vencer_30d: 2,
};

export const mockRutas = [
  {
    id: 1, codigo: "SIT-1", nombre: "Naranjal - Matellini", tipo: "regular",
    hora_inicio: "05:00", hora_fin: "23:00", frecuencia_min: 10, activa: true,
  },
  {
    id: 2, codigo: "N-205", nombre: "Nocturna Centro", tipo: "nocturna",
    hora_inicio: "23:00", hora_fin: "04:30", frecuencia_min: 30, activa: false,
  },
];

export const mockEstaciones = [
  {
    id: 1, codigo: "EST-001", nombre: "Estación Naranjal", tipo: "terminal",
    tramo: "norte", orden_troncal: 1, activa: true,
  },
  {
    id: 2, codigo: "EST-014", nombre: "Estación Central", tipo: "transferencia",
    tramo: "centro", orden_troncal: 14, activa: true,
  },
];

export const mockAlertasDoc = [
  {
    chofer_id: 7, nombres: "Juan", apellidos: "Pérez García",
    estado: "VENCIDA", dias_certif: 0, fec_vence_certif_prot: "2026-06-01",
  },
  {
    chofer_id: 9, nombres: "Rosa", apellidos: "Quispe Mamani",
    estado: "POR_VENCER", dias_certif: 12, fec_vence_certif_prot: "2026-06-23",
  },
];

// Programación siempre vigente: Grilla autoselecciona la que cubre la fecha de hoy
const hoy = new Date();
const isoOffset = (dias) => {
  const d = new Date(hoy);
  d.setDate(d.getDate() + dias);
  return d.toISOString().slice(0, 10);
};

export const mockProgramaciones = [
  {
    id: 1, nombre: "Semana actual", estado: "borrador",
    fecha_inicio: isoOffset(-3), fecha_fin: isoOffset(3), observaciones: null,
  },
];

export const mockHorarios = [
  {
    id: 11, ruta_id: 1, fecha: isoOffset(0), hora_salida: "05:00", turno: "manana",
    duracion_est_min: 90, activo: true, asignacion_id: 501,
    chofer: { id: 7, nombre: "Juan Pérez" }, conflicto: null,
  },
  {
    id: 12, ruta_id: 1, fecha: isoOffset(0), hora_salida: "14:00", turno: "tarde",
    duracion_est_min: 90, activo: true, asignacion_id: null,
    chofer: null, conflicto: null,
  },
];

export const mockAreas = [
  { id: 1, nombre: "Operaciones Norte", nombre_corto: "Op. Norte", activo: true },
  { id: 2, nombre: "Operaciones Sur", nombre_corto: "Op. Sur", activo: true },
];

export const mockChoferes = [
  { id: 7, nombres: "Juan", apellidos: "Pérez García", numero_licencia: "LIC-001", area_id: 1, estado: "activo" },
  { id: 9, nombres: "Rosa", apellidos: "Quispe Mamani", numero_licencia: "LIC-002", area_id: 2, estado: "activo" },
];

export const mockBuses = [
  { placa: "ABC-123", tipo: "articulado", area_id: 1, estado: "operativo" },
  { placa: "DEF-456", tipo: "convencional", area_id: 2, estado: "operativo" },
];

// ── Seeds del Copiloto IA (RF05) ────────────────────────────────────
export const mockAlertasFatiga = {
  total: 1,
  alertas: [
    {
      chofer_id: 7, nombres: "Juan", apellidos: "Pérez García",
      tipo: "descanso_insuficiente", severidad: "media",
      alerta: "Menos de 10h entre turnos el " + isoOffset(1),
      sugerencia: "Reprograma el turno de la mañana o asigna un reemplazo.",
      fecha_referencia: isoOffset(1),
    },
  ],
  actualizado_en: Math.floor(Date.now() / 1000),
};

export const mockAsigSelector = [
  { asignacion_id: 501, label: "Juan Pérez García — Mañana · SIT-1", tiene_problema: false },
  { asignacion_id: 502, label: "Rosa Quispe Mamani — Tarde · SIT-1", tiene_problema: true },
];

export const mockSugerenciaReemplazo = {
  asignacion_id: 502,
  horario: { turno: "tarde", fecha: isoOffset(0), ruta_nombre: "SIT-1" },
  chofer_ausente: { id: 9, nombres: "Rosa", apellidos: "Quispe Mamani" },
  candidatos_evaluados: 3,
  recomendacion_ia: {
    recomendacion: "Juan Pérez García tiene la menor carga horaria y licencia vigente.",
    chofer_id_recomendado: 7,
  },
};

export const mockAplicarReemplazo = {
  asignacion_nueva_id: 900,
  chofer_reemplazo: { id: 7, nombres: "Juan", apellidos: "Pérez García" },
  recomendacion: "Reasignado por menor carga horaria.",
  horario: { fecha: isoOffset(0) },
};

export const mockChatRespuesta = {
  intent: "disponibilidad",
  respuesta: "Hay 2 choferes disponibles el viernes tarde en el área norte.",
};

// ── Handlers por defecto (solo lecturas felices) ───────────────────
// Las escrituras y los casos de error se sobreescriben por test con server.use(...)
export const handlers = [
  // Login OK por defecto. Tests pueden sobreescribir con server.use(...)
  http.post(`${API}/api/auth/login`, async ({ request }) => {
    const form = await request.formData();
    const username = form.get("username");
    const password = form.get("password");

    if (username === "admin.atu@metrohub.gob.pe" && password === "admin123") {
      return HttpResponse.json({
        access_token: "fake-jwt-admin",
        token_type: "bearer",
        rol: "admin_atu",
        nombre: "Admin ATU",
        chofer_id: null,
        area_id: null,
        debe_cambiar_password: false,
      });
    }
    return new HttpResponse(JSON.stringify({ detail: "Credenciales incorrectas" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }),

  http.get(`${API}/api/dashboard`, () => HttpResponse.json(mockKpis)),

  // El mismo handler atiende /api/rutas y /api/rutas?solo_activas=true
  http.get(`${API}/api/rutas`, ({ request }) => {
    const soloActivas = new URL(request.url).searchParams.get("solo_activas") === "true";
    return HttpResponse.json(soloActivas ? mockRutas.filter(r => r.activa) : mockRutas);
  }),

  http.get(`${API}/api/rutas/:id/estaciones`, () => HttpResponse.json([])),

  http.get(`${API}/api/estaciones`, () =>
    HttpResponse.json({ total: mockEstaciones.length, estaciones: mockEstaciones })),

  http.get(`${API}/api/choferes/alertas/documentos`, () =>
    HttpResponse.json({ total: mockAlertasDoc.length, choferes: mockAlertasDoc })),

  http.get(`${API}/api/choferes`, () => HttpResponse.json(mockChoferes)),

  http.get(`${API}/api/programaciones`, () =>
    HttpResponse.json({ total: mockProgramaciones.length, programaciones: mockProgramaciones })),

  http.get(`${API}/api/horarios`, () =>
    HttpResponse.json({ total: mockHorarios.length, horarios: mockHorarios })),

  http.get(`${API}/api/areas`, () =>
    HttpResponse.json({ total: mockAreas.length, areas: mockAreas })),

  http.get(`${API}/api/buses`, () =>
    HttpResponse.json({ total: mockBuses.length, buses: mockBuses })),

  // Copiloto IA (RF05)
  http.get(`${API}/api/ia/alertas-fatiga`, () => HttpResponse.json(mockAlertasFatiga)),
  http.get(`${API}/api/ia/asignaciones-selector`, () => HttpResponse.json(mockAsigSelector)),
  http.post(`${API}/api/ia/sugerir-reemplazo/:id`, () => HttpResponse.json(mockSugerenciaReemplazo)),
  http.post(`${API}/api/ia/aplicar-reemplazo/:id`, () => HttpResponse.json(mockAplicarReemplazo)),
  http.post(`${API}/api/ia/programar-descanso/:choferId`, async ({ request, params }) => {
    const body = await request.json();
    return HttpResponse.json({
      mensaje: "Descanso registrado", fecha: body.fecha,
      chofer_id: Number(params.choferId), turnos_liberados: 1,
    });
  }),
  http.post(`${API}/api/ia/chat`, () => HttpResponse.json(mockChatRespuesta)),
];
