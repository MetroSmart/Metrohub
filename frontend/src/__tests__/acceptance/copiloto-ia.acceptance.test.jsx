import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  mockAlertasFatiga, mockSugerenciaReemplazo, mockAplicarReemplazo, mockChatRespuesta,
} from "../../test/handlers.js";
import CopilotoIA from "../../components/CopilotoIA.jsx";

const SUPERVISOR = { role: "supervisor_area", name: "Sup Norte", area_id: 1 };
const CHOFER = { role: "chofer", name: "Juan Pérez" };

// Nivel de aceptación: un escenario por criterio de RF05 (Copiloto IA),
// redactado en Given/When/Then. No se prueba el wireup de App.jsx — el
// Copiloto se ejercita como lo recibiría (props que Grilla/App ya le pasan).
describe("Criterios de aceptación — Copiloto IA (RF05)", () => {
  it("Dado un supervisor con una alerta de fatiga, cuando registra el descanso, entonces ve la confirmación y el acceso directo a la Grilla", async () => {
    const onNavToGrilla = vi.fn();
    const user = userEvent.setup();
    render(<CopilotoIA user={SUPERVISOR} onNavToGrilla={onNavToGrilla} />);

    // Given: abre el panel y ve la alerta de fatiga de su área
    await user.click(screen.getByTitle("Copiloto IA"));
    const alerta = mockAlertasFatiga.alertas[0];
    await screen.findByText(`${alerta.nombres} ${alerta.apellidos}`);

    // When: registra el descanso desde el botón de acción de la alerta
    await user.click(screen.getByRole("button", { name: "😴 Dar descanso compensatorio" }));

    // Then: confirmación con turnos liberados y acceso directo a la Grilla
    expect(await screen.findByText(/Descanso registrado para/)).toBeInTheDocument();
    const irAGrilla = screen.getByRole("button", { name: "Ver turnos del día en Grilla →" });
    await user.click(irAGrilla);
    expect(onNavToGrilla).toHaveBeenCalledWith(alerta.fecha_referencia);
  });

  it("Dado que la Grilla dispara un reemplazo para una asignación con conflicto, cuando el Copiloto se abre, entonces la sugerencia se carga y se aplica sin pasos adicionales", async () => {
    const user = userEvent.setup();
    render(<CopilotoIA user={SUPERVISOR} reemplazoTrigger={{ asigId: 502 }} />);

    // Given/When: el trigger ya dejó el panel abierto en Reemplazo con la sugerencia cargada
    expect(
      await screen.findByText(`Recomendación IA (${mockSugerenciaReemplazo.candidatos_evaluados} candidatos evaluados)`),
    ).toBeInTheDocument();

    // Then: se aplica con un clic, sin buscar manualmente un chofer disponible
    await user.click(screen.getByRole("button", { name: "🚀 Aplicar este reemplazo" }));
    expect(await screen.findByText("✅ Reemplazo aplicado")).toBeInTheDocument();
    expect(screen.getByText(
      `${mockAplicarReemplazo.chofer_reemplazo.nombres} ${mockAplicarReemplazo.chofer_reemplazo.apellidos}`,
      { selector: "strong" },
    )).toBeInTheDocument();
  });

  it("Dado un usuario autorizado en la pestaña Asistente, cuando pregunta sobre disponibilidad, entonces recibe una respuesta en lenguaje natural", async () => {
    const user = userEvent.setup();
    render(<CopilotoIA user={SUPERVISOR} />);

    await user.click(screen.getByTitle("Copiloto IA"));
    await user.click(screen.getByRole("button", { name: "💬 Asistente" }));
    await user.click(screen.getByRole("button", { name: "¿Quién está disponible?" }));
    await user.type(
      screen.getByRole("textbox"),
      "¿Quién está libre el viernes tarde en área norte?",
    );
    await user.click(screen.getByRole("button", { name: "✉️ Preguntar" }));

    expect(await screen.findByText(mockChatRespuesta.respuesta)).toBeInTheDocument();
  });

  it("Dado un usuario con rol chofer, entonces el Copiloto IA no está disponible (no es una herramienta operativa para ese rol)", () => {
    render(<CopilotoIA user={CHOFER} />);
    expect(screen.queryByTitle("Copiloto IA")).not.toBeInTheDocument();
  });
});
