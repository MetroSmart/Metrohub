import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import MisRutas from "../../pages/MisRutas.jsx";

const CHOFER = { role: "chofer", name: "Juan Pérez" };
const API = "http://localhost:8000";

const ASIGNACIONES = {
  chofer_nombre: "Juan Pérez García",
  asignaciones: [
    {
      asignacion_id: 501, es_siguiente: true, estado: "confirmada", bus_placa: "ABC-123",
      ruta: { codigo: "SIT-1", nombre: "Naranjal - Matellini" },
      horario: { hora_salida: "05:00", turno: "manana", duracion_est_min: 90 },
      estaciones: [
        { estacion_id: 1, orden: 1, codigo: "EST-001", nombre: "Estación Naranjal", tiempo_est_min: null },
        { estacion_id: 2, orden: 2, codigo: "EST-014", nombre: "Estación Central", tiempo_est_min: 25 },
      ],
    },
    {
      asignacion_id: 502, es_siguiente: false, estado: "propuesta", bus_placa: null,
      ruta: { codigo: "N-205", nombre: "Nocturna Centro" },
      horario: { hora_salida: "23:00", turno: "noche", duracion_est_min: 60 },
      estaciones: [],
    },
  ],
};

let fechasPedidas;

beforeEach(() => {
  fechasPedidas = [];
  server.use(
    http.get(`${API}/api/choferes/me/asignaciones`, ({ request }) => {
      fechasPedidas.push(new URL(request.url).searchParams.get("fecha"));
      return HttpResponse.json(ASIGNACIONES);
    }),
  );
});

function setup() {
  return render(<MisRutas user={CHOFER} onNav={() => {}} onLogout={() => {}} />);
}

describe("MisRutas (RF04 — vista chofer)", () => {
  it("muestra el próximo servicio con turno, bus y duración", async () => {
    setup();
    expect(await screen.findByText("Ruta SIT-1 — Naranjal - Matellini")).toBeInTheDocument();
    expect(screen.getByText("Próximo servicio")).toBeInTheDocument();
    expect(screen.getByText("Chofer: Juan Pérez García")).toBeInTheDocument();
    expect(screen.getAllByText("05:00").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Mañana").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Bus ABC-123")).toBeInTheDocument();
    expect(screen.getByText("90 min")).toBeInTheDocument();
  });

  it("lista las estaciones de la ruta del próximo servicio", async () => {
    setup();
    expect(await screen.findByText("Estación Naranjal")).toBeInTheDocument();
    expect(screen.getByText("Estación Central")).toBeInTheDocument();
    expect(screen.getByText("Parada 1")).toBeInTheDocument();
    expect(screen.getByText("Parada 2 · +25 min")).toBeInTheDocument();
  });

  it("muestra la tabla con todos los servicios del día", async () => {
    setup();
    expect(await screen.findByText("Todos mis servicios (2)")).toBeInTheDocument();
    expect(screen.getByText("N-205")).toBeInTheDocument();
    expect(screen.getByText("Nocturna Centro")).toBeInTheDocument();
    expect(screen.getByText("Noche")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument(); // servicio sin bus asignado
  });

  it("muestra el mensaje vacío cuando no hay asignaciones", async () => {
    server.use(
      http.get(`${API}/api/choferes/me/asignaciones`, () =>
        HttpResponse.json({ chofer_nombre: "Juan Pérez García", asignaciones: [] }),
      ),
    );
    setup();
    expect(
      await screen.findByText("No tienes rutas asignadas para esta fecha."),
    ).toBeInTheDocument();
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/choferes/me/asignaciones`, () =>
        HttpResponse.json({ detail: "Token inválido" }, { status: 401 }),
      ),
    );
    setup();
    expect(await screen.findByText("Token inválido")).toBeInTheDocument();
  });

  it("al cambiar la fecha vuelve a consultar el API con la nueva fecha", async () => {
    const { container } = setup();
    await screen.findByText("Todos mis servicios (2)");

    const dateInput = container.querySelector('input[type="date"]');
    fireEvent.change(dateInput, { target: { value: "2026-06-15" } });

    await screen.findByText("Todos mis servicios (2)");
    expect(fechasPedidas).toContain("2026-06-15");
  });
});
