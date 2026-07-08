import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import {
  mockAlertasFatiga, mockAsigSelector, mockSugerenciaReemplazo,
  mockAplicarReemplazo, mockChatRespuesta,
} from "../../test/handlers.js";
import CopilotoIA from "../../components/CopilotoIA.jsx";

const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const API = "http://localhost:8000";

afterEach(() => {
  vi.restoreAllMocks();
});

// Nivel de sistema: CopilotoIA como subsistema completo (UI + api.js + red vía
// MSW, sin mocks de módulo), recorriendo sus tres pestañas en un solo flujo
// continuo tal como lo haría un usuario real.
describe("Copiloto IA — flujo de sistema (RF05)", () => {
  it("recorre fatiga → reemplazo → asistente contra la red real (MSW)", async () => {
    const user = userEvent.setup();
    render(<CopilotoIA user={ADMIN} />);

    // 1) Se abre y trae las alertas de fatiga desde el backend
    await user.click(screen.getByTitle("Copiloto IA"));
    const alerta = mockAlertasFatiga.alertas[0];
    expect(await screen.findByText(`${alerta.nombres} ${alerta.apellidos}`)).toBeInTheDocument();
    expect(screen.getByText(alerta.severidad.toUpperCase())).toBeInTheDocument();

    // 2) Cambia a Reemplazo: carga el selector real y pide + aplica la sugerencia IA
    await user.click(screen.getByRole("button", { name: "🔄 Reemplazo" }));
    const opcion = mockAsigSelector[0];
    await user.selectOptions(
      await screen.findByDisplayValue("— Selecciona una asignación —"),
      String(opcion.asignacion_id),
    );
    await user.click(screen.getByRole("button", { name: "🔍 Sugerir reemplazo" }));
    expect(
      await screen.findByText(`Recomendación IA (${mockSugerenciaReemplazo.candidatos_evaluados} candidatos evaluados)`),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "🚀 Aplicar este reemplazo" }));
    expect(await screen.findByText("✅ Reemplazo aplicado")).toBeInTheDocument();
    expect(screen.getByText(
      `${mockAplicarReemplazo.chofer_reemplazo.nombres} ${mockAplicarReemplazo.chofer_reemplazo.apellidos}`,
      { selector: "strong" },
    )).toBeInTheDocument();

    // 3) Cambia a Asistente: pregunta y recibe la respuesta real del backend
    await user.click(screen.getByRole("button", { name: "💬 Asistente" }));
    await user.type(screen.getByRole("textbox"), "¿Cómo va la programación de esta semana?");
    await user.click(screen.getByRole("button", { name: "✉️ Preguntar" }));
    expect(await screen.findByText(mockChatRespuesta.respuesta)).toBeInTheDocument();
  });

  it("se degrada a un mensaje de error sin romperse cuando el servicio IA falla (RNF04)", async () => {
    server.use(
      http.get(`${API}/api/ia/alertas-fatiga`, () =>
        new HttpResponse(JSON.stringify({ detail: "Servicio IA no disponible" }), {
          status: 503, headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const user = userEvent.setup();
    render(<CopilotoIA user={ADMIN} />);

    await user.click(screen.getByTitle("Copiloto IA"));

    expect(await screen.findByText(/Servicio IA no disponible/)).toBeInTheDocument();
    // El panel sigue operable: las otras pestañas no se ven afectadas
    await user.click(screen.getByRole("button", { name: "💬 Asistente" }));
    expect(screen.getByRole("button", { name: "✉️ Preguntar" })).toBeInTheDocument();
  });
});
