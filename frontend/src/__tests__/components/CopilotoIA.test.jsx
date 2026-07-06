import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CopilotoIA from "../../components/CopilotoIA.jsx";
import { api } from "../../api";

vi.mock("../../api", () => ({
  api: { get: vi.fn(), post: vi.fn() },
}));

const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const CHOFER = { role: "chofer", name: "Juan Pérez" };

const ALERTA_DESCANSO = {
  chofer_id: 7, nombres: "Rosa", apellidos: "Quispe Mamani",
  tipo: "descanso_insuficiente", severidad: "media",
  alerta: "Menos de 10h entre turnos el 2026-07-11",
  sugerencia: "Reprograma el turno de la mañana o asigna un reemplazo.",
  fecha_referencia: "2026-07-11",
};

const ASIG_OPCIONES = [
  { asignacion_id: 501, label: "Rosa Quispe Mamani — Mañana · SIT-1", tiene_problema: false },
];

const SUGERENCIA_REEMPLAZO = {
  asignacion_id: 501,
  horario: { turno: "manana", fecha: "2026-07-11", ruta_nombre: "SIT-1" },
  chofer_ausente: { id: 7, nombres: "Rosa", apellidos: "Quispe Mamani" },
  candidatos_evaluados: 3,
  recomendacion_ia: {
    recomendacion: "Juan Pérez tiene la menor carga horaria disponible.",
    chofer_id_recomendado: 9,
  },
};

const APLICAR_REEMPLAZO = {
  asignacion_nueva_id: 900,
  chofer_reemplazo: { id: 9, nombres: "Juan", apellidos: "Pérez" },
  recomendacion: "Reasignado por menor carga horaria.",
  horario: { fecha: "2026-07-11" },
};

function setup(props = {}) {
  return render(<CopilotoIA user={ADMIN} {...props} />);
}

async function abrirPanel(user, props = {}) {
  const utils = setup(props);
  await user.click(screen.getByTitle("Copiloto IA"));
  return utils;
}

describe("CopilotoIA (RF05 — asistente de programación)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({ total: 0, alertas: [], actualizado_en: 0 });
  });

  it("no renderiza el botón flotante sin usuario o con rol chofer", () => {
    const { rerender } = render(<CopilotoIA user={null} />);
    expect(screen.queryByTitle("Copiloto IA")).not.toBeInTheDocument();

    rerender(<CopilotoIA user={CHOFER} />);
    expect(screen.queryByTitle("Copiloto IA")).not.toBeInTheDocument();
  });

  it("abre el panel y carga las alertas de fatiga automáticamente", async () => {
    const user = userEvent.setup();
    await abrirPanel(user);

    expect(screen.getByText("Alertas de esta semana")).toBeInTheDocument();
    expect(await screen.findByText("✅ Sin alertas detectadas esta semana")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith("/api/ia/alertas-fatiga");
  });

  it("renderiza una alerta con severidad y el botón de acción según el tipo", async () => {
    api.get.mockResolvedValue({ total: 1, alertas: [ALERTA_DESCANSO], actualizado_en: 0 });
    const user = userEvent.setup();
    await abrirPanel(user);

    expect(await screen.findByText("Rosa Quispe Mamani")).toBeInTheDocument();
    expect(screen.getByText("MEDIA")).toBeInTheDocument();
    expect(screen.getByText(ALERTA_DESCANSO.alerta)).toBeInTheDocument();
    expect(screen.getByText(`💡 ${ALERTA_DESCANSO.sugerencia}`)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "😴 Dar descanso compensatorio" })).toBeInTheDocument();
  });

  it("registra el descanso y muestra la confirmación con turnos liberados", async () => {
    api.get.mockResolvedValue({ total: 1, alertas: [ALERTA_DESCANSO], actualizado_en: 0 });
    api.post.mockResolvedValueOnce({ mensaje: "Descanso registrado", turnos_liberados: 2 });
    const user = userEvent.setup();
    await abrirPanel(user);
    await screen.findByText("Rosa Quispe Mamani");

    await user.click(screen.getByRole("button", { name: "😴 Dar descanso compensatorio" }));

    expect(api.post).toHaveBeenCalledWith("/api/ia/programar-descanso/7", {
      fecha: "2026-07-11", observaciones: "",
    });
    expect(await screen.findByText(/2 turnos liberados/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "✅ Aplicado" })).toBeInTheDocument();
  });

  it("tab Reemplazo: exige seleccionar una asignación y sugiere un reemplazo", async () => {
    api.get.mockResolvedValue(ASIG_OPCIONES);
    const user = userEvent.setup();
    await abrirPanel(user);

    await user.click(screen.getByRole("button", { name: "🔄 Reemplazo" }));
    await screen.findByDisplayValue("— Selecciona una asignación —");

    await user.click(screen.getByRole("button", { name: "🔍 Sugerir reemplazo" }));
    expect(await screen.findByText(/Selecciona una asignación de la lista/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();

    api.post.mockResolvedValueOnce(SUGERENCIA_REEMPLAZO);
    await user.selectOptions(screen.getByRole("combobox"), "501");
    await user.click(screen.getByRole("button", { name: "🔍 Sugerir reemplazo" }));

    expect(await screen.findByText("Recomendación IA (3 candidatos evaluados)")).toBeInTheDocument();
    expect(screen.getByText(SUGERENCIA_REEMPLAZO.recomendacion_ia.recomendacion)).toBeInTheDocument();
  });

  it("tab Reemplazo: aplica el reemplazo sugerido", async () => {
    api.get.mockResolvedValue(ASIG_OPCIONES);
    api.post.mockResolvedValueOnce(SUGERENCIA_REEMPLAZO);
    const user = userEvent.setup();
    await abrirPanel(user);
    await user.click(screen.getByRole("button", { name: "🔄 Reemplazo" }));
    await user.selectOptions(await screen.findByRole("combobox"), "501");
    await user.click(screen.getByRole("button", { name: "🔍 Sugerir reemplazo" }));
    await screen.findByText("Recomendación IA (3 candidatos evaluados)");

    api.post.mockResolvedValueOnce(APLICAR_REEMPLAZO);
    await user.click(screen.getByRole("button", { name: "🚀 Aplicar este reemplazo" }));

    expect(await screen.findByText("✅ Reemplazo aplicado")).toBeInTheDocument();
    expect(screen.getByText(
      `${APLICAR_REEMPLAZO.chofer_reemplazo.nombres} ${APLICAR_REEMPLAZO.chofer_reemplazo.apellidos}`,
      { selector: "strong" },
    )).toBeInTheDocument();
  });

  it("tab Asistente: exige una pregunta y muestra la respuesta del API", async () => {
    const user = userEvent.setup();
    await abrirPanel(user);

    await user.click(screen.getByRole("button", { name: "💬 Asistente" }));
    await user.click(screen.getByRole("button", { name: "✉️ Preguntar" }));
    expect(await screen.findByText(/Escribe una pregunta/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();

    api.post.mockResolvedValueOnce({ intent: "disponibilidad", respuesta: "Hay 2 choferes libres el viernes." });
    await user.type(screen.getByRole("textbox"), "¿Quién está libre el viernes?");
    await user.click(screen.getByRole("button", { name: "✉️ Preguntar" }));

    expect(api.post).toHaveBeenCalledWith("/api/ia/chat", {
      intent: "disponibilidad", pregunta: "¿Quién está libre el viernes?", params: {},
    });
    expect(await screen.findByText("Hay 2 choferes libres el viernes.")).toBeInTheDocument();
  });

  it("muestra un error cuando la API falla", async () => {
    api.get.mockRejectedValueOnce(new Error("Servicio IA no disponible"));
    const user = userEvent.setup();
    await abrirPanel(user);

    expect(await screen.findByText("⚠️ Servicio IA no disponible")).toBeInTheDocument();
  });

  it("reemplazoTrigger abre el panel en la pestaña Reemplazo con la sugerencia precargada", async () => {
    api.get.mockResolvedValue(ASIG_OPCIONES);
    api.post.mockResolvedValueOnce(SUGERENCIA_REEMPLAZO);

    setup({ reemplazoTrigger: { asigId: 501 } });

    expect(await screen.findByText("Recomendación IA (3 candidatos evaluados)")).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith("/api/ia/sugerir-reemplazo/501");
  });
});
