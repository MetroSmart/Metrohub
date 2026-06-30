import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Grilla from "../../pages/Grilla.jsx";

const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const SUPERVISOR = { role: "supervisor_area", name: "Sup Norte", area_id: 1 };
const API = "http://localhost:8000";
const HOY = new Date().toISOString().slice(0, 10);

const HORARIO_CONFLICTO = {
  id: 13, ruta_id: 1, fecha: HOY, hora_salida: "08:00", turno: "manana",
  duracion_est_min: 90, activo: true, asignacion_id: 502,
  chofer: { id: 9, nombre: "Rosa Quispe" },
  conflicto: {
    id: 5, tipo: "doble_asignacion", severidad: "alta",
    descripcion: "Chofer asignado a dos horarios simultáneos",
  },
};

function setup(user = ADMIN) {
  return render(<Grilla user={user} onNav={() => {}} onLogout={() => {}} />);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Grilla (RF04/RF05 — programación de horarios)", () => {
  it("autoselecciona la programación vigente y lista los horarios", async () => {
    setup();
    // mockHorarios: 05:00 asignado a Juan Pérez, 14:00 sin asignar
    expect(await screen.findByText("05:00")).toBeInTheDocument();
    expect(screen.getByText("14:00")).toBeInTheDocument();
    expect(screen.getByDisplayValue(/Semana actual/)).toBeInTheDocument();
    expect(screen.getByText("borrador")).toBeInTheDocument();
    expect(screen.getByText("Juan Pérez")).toBeInTheDocument();
    expect(screen.getByText("Sin asignar")).toBeInTheDocument();
    expect(screen.getByText("Mañana")).toBeInTheDocument();
    expect(screen.getByText("Tarde")).toBeInTheDocument();
    expect(screen.getAllByText("SIT-1").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/2 horarios para .*Sin conflictos\./)).toBeInTheDocument();
  });

  it("muestra los conflictos y el admin puede resolverlos", async () => {
    server.use(
      http.get(`${API}/api/horarios`, () =>
        HttpResponse.json({ total: 1, horarios: [HORARIO_CONFLICTO] }),
      ),
      http.patch(`${API}/api/conflictos/5/resolver`, () => HttpResponse.json({ ok: true })),
    );
    const user = userEvent.setup();
    setup();

    expect(await screen.findByText("Conflicto")).toBeInTheDocument();
    expect(screen.getByText("doble asignacion")).toBeInTheDocument();
    expect(screen.getByText("Chofer asignado a dos horarios simultáneos")).toBeInTheDocument();
    expect(screen.getByText("1 conflicto")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Resolver" }));

    await vi.waitFor(() =>
      expect(screen.queryByText("Conflicto")).not.toBeInTheDocument(),
    );
    expect(screen.getByText(/Sin conflictos\./)).toBeInTheDocument();
  });

  it("asigna un chofer a un horario sin cubrir", async () => {
    let body;
    server.use(
      http.post(`${API}/api/horarios/asignaciones`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 900 }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("05:00");

    await user.click(screen.getByRole("button", { name: "Asignar" }));
    expect(await screen.findByText("Asignar chofer")).toBeInTheDocument();

    // Validación con el formulario vacío
    await user.click(screen.getByRole("button", { name: "Confirmar asignación" }));
    expect(await screen.findByText("Chofer y área son obligatorios.")).toBeInTheDocument();

    await user.selectOptions(
      await screen.findByDisplayValue("— Selecciona un chofer —"), "7",
    );
    await user.selectOptions(screen.getByDisplayValue("— Selecciona un área —"), "1");
    await user.click(screen.getByRole("button", { name: "Confirmar asignación" }));

    await vi.waitFor(() =>
      expect(screen.queryByText("Asignar chofer")).not.toBeInTheDocument(),
    );
    expect(body).toEqual({
      horario_id: 12, chofer_id: 7, area_id: 1, bus_placa: null, notas: null,
    });
  });

  it("quita la asignación de un chofer tras confirmar", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    server.use(
      http.delete(`${API}/api/horarios/asignaciones/501`, () =>
        new HttpResponse(null, { status: 204 }),
      ),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Juan Pérez");

    await user.click(screen.getByRole("button", { name: "Quitar" }));

    await vi.waitFor(() =>
      expect(screen.queryByText("Juan Pérez")).not.toBeInTheDocument(),
    );
    expect(screen.getAllByText("Sin asignar")).toHaveLength(2);
  });

  it("aprueba la programación y actualiza su estado", async () => {
    let urlPedida;
    server.use(
      http.patch(`${API}/api/horarios/programacion/1/estado`, ({ request }) => {
        urlPedida = request.url;
        return HttpResponse.json({ ok: true });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("05:00");

    await user.click(screen.getByRole("button", { name: "Aprobar programación" }));

    expect(
      await screen.findByText('Programación marcada como "aprobada".'),
    ).toBeInTheDocument();
    expect(screen.getByText("aprobada")).toBeInTheDocument();
    expect(urlPedida).toContain("estado=aprobada");
  });

  it("crea una programación nueva y la deja seleccionada", async () => {
    let body;
    server.use(
      http.post(`${API}/api/programaciones`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 2, ...body, estado: "borrador" }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    const { baseElement } = setup();
    await screen.findByText("05:00");

    await user.click(screen.getByRole("button", { name: "+ Nueva programación" }));

    await user.click(screen.getByRole("button", { name: "Crear programación" }));
    expect(
      await screen.findByText("Nombre, fecha de inicio y fecha fin son obligatorios."),
    ).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("Ej. Programación Semana 23"), "Semana próxima");
    // Inputs de fecha: [0] es el filtro de la página; [1] y [2] son los del modal
    const fechas = baseElement.querySelectorAll('input[type="date"]');
    fireEvent.change(fechas[1], { target: { value: "2026-06-15" } });
    fireEvent.change(fechas[2], { target: { value: "2026-06-21" } });
    await user.click(screen.getByRole("button", { name: "Crear programación" }));

    expect(await screen.findByDisplayValue(/Semana próxima/)).toBeInTheDocument();
    expect(body).toEqual({
      nombre: "Semana próxima", fecha_inicio: "2026-06-15",
      fecha_fin: "2026-06-21", observaciones: null,
    });
  });

  it("agrega un horario a la programación seleccionada", async () => {
    let body;
    server.use(
      http.post(`${API}/api/horarios`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 99, ...body }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    const { baseElement } = setup();
    await screen.findByText("05:00");

    await user.click(screen.getByRole("button", { name: "+ Agregar horario" }));

    // Sin ruta ni hora de salida todavía
    await user.click(screen.getByRole("button", { name: "Agregar horario" }));
    expect(
      await screen.findByText("Ruta, fecha y hora de salida son obligatorios."),
    ).toBeInTheDocument();

    await user.selectOptions(screen.getByDisplayValue("— Selecciona una ruta —"), "1");
    fireEvent.change(baseElement.querySelector('input[type="time"]'), {
      target: { value: "06:30" },
    });
    await user.click(screen.getByRole("button", { name: "Agregar horario" }));

    await vi.waitFor(() => expect(body).toBeDefined());
    expect(body).toEqual({
      programacion_id: 1, ruta_id: 1, fecha: HOY,
      hora_salida: "06:30", turno: "manana", duracion_est_min: 60,
    });
  });

  it("duplica la semana e informa el resultado", async () => {
    let body;
    server.use(
      http.post(`${API}/api/horarios/duplicar-semana`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({
          horarios_duplicados: 12, asignaciones_duplicadas: 8, advertencias: [],
        });
      }),
    );
    const user = userEvent.setup();
    const { baseElement } = setup();
    await screen.findByText("05:00");

    await user.click(screen.getByRole("button", { name: "Duplicar semana" }));

    // Solo viene la semana origen precargada
    await user.click(screen.getByRole("button", { name: "Duplicar" }));
    expect(await screen.findByText("Ambas fechas son obligatorias.")).toBeInTheDocument();

    const fechas = baseElement.querySelectorAll('input[type="date"]');
    fireEvent.change(fechas[2], { target: { value: "2026-06-22" } }); // destino
    await user.click(screen.getByRole("button", { name: "Duplicar" }));

    expect(
      await screen.findByText(/Duplicado: 12 horarios, 8 asignaciones\./),
    ).toBeInTheDocument();
    expect(body).toMatchObject({
      fecha_inicio_destino: "2026-06-22",
      incluir_asignaciones: true,
      omitir_existentes: true,
    });
  });

  it("elimina un horario tras confirmar", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    server.use(
      http.delete(`${API}/api/horarios/11`, () => new HttpResponse(null, { status: 204 })),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("05:00");

    await user.click(screen.getAllByRole("button", { name: "Eliminar horario" })[0]);

    await vi.waitFor(() =>
      expect(screen.queryByText("05:00")).not.toBeInTheDocument(),
    );
    expect(screen.getByText("14:00")).toBeInTheDocument();
  });

  it("supervisor solo puede asignar choferes, sin acciones de admin", async () => {
    setup(SUPERVISOR);
    await screen.findByText("05:00");

    expect(screen.getByRole("button", { name: "Asignar" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "+ Nueva programación" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Aprobar programación" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Duplicar semana" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "+ Agregar horario" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Eliminar horario" })).not.toBeInTheDocument();
  });
});
