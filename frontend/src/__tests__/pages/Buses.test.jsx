import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Buses from "../../pages/Buses.jsx";

const ADMIN = { role: "admin_atu", name: "Ana Torres" };
const SUPERVISOR = { role: "supervisor_area", name: "Supervisor Norte", area_id: 1 };
const API = "http://localhost:8000";

function setup(user = ADMIN) {
  return render(<Buses user={user} onNav={() => {}} onLogout={() => {}} />);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Buses (RF09 — flota)", () => {
  it("lista los buses con placa, tipo, área y estado", async () => {
    setup();
    expect(await screen.findByText("ABC-123")).toBeInTheDocument();
    expect(screen.getByText("DEF-456")).toBeInTheDocument();
    expect(screen.getByText("articulado")).toBeInTheDocument();
    expect(screen.getByText("convencional")).toBeInTheDocument();
    expect(await screen.findByText("Op. Norte")).toBeInTheDocument();
    expect(screen.getByText("Op. Sur")).toBeInTheDocument();
    expect(screen.getAllByText("operativo")).toHaveLength(2);
    expect(screen.getByText("2 buses en total")).toBeInTheDocument();
  });

  it("filtra por estado consultando al API", async () => {
    const estadosPedidos = [];
    server.use(
      http.get(`${API}/api/buses`, ({ request }) => {
        estadosPedidos.push(new URL(request.url).searchParams.get("estado"));
        return HttpResponse.json({ total: 0, buses: [] });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Sin buses registrados.");

    await user.selectOptions(screen.getByDisplayValue("Todos los estados"), "mantenimiento");

    await vi.waitFor(() => expect(estadosPedidos).toContain("mantenimiento"));
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/buses`, () =>
        HttpResponse.json({ detail: "Servicio no disponible" }, { status: 503 }),
      ),
    );
    setup();
    expect(await screen.findByText(/error al cargar: servicio no disponible/i)).toBeInTheDocument();
  });

  it("valida placa y área obligatorios al registrar", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("ABC-123");

    await user.click(screen.getByRole("button", { name: "+ Registrar bus" }));
    await user.click(screen.getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText("Placa y área son obligatorios.")).toBeInTheDocument();
  });

  it("registra un bus normalizando la placa a mayúsculas", async () => {
    let body;
    server.use(
      http.post(`${API}/api/buses`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ ...body }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("ABC-123");

    await user.click(screen.getByRole("button", { name: "+ Registrar bus" }));
    await user.type(screen.getByPlaceholderText("Ej. ABC-123"), "ghi-789");
    await user.selectOptions(screen.getByDisplayValue("— Seleccionar —"), "1");
    await user.click(screen.getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText("GHI-789")).toBeInTheDocument();
    expect(screen.getByText("3 buses en total")).toBeInTheDocument();
    expect(body).toEqual({
      placa: "GHI-789", area_id: 1, tipo: "articulado",
      anio: null, capacidad_pasajeros: null, estado: "operativo",
    });
  });

  it("cambia el estado de un bus desde la fila", async () => {
    server.use(
      http.patch(`${API}/api/buses/ABC-123`, async ({ request }) => {
        const { estado } = await request.json();
        return HttpResponse.json({ placa: "ABC-123", estado });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("ABC-123");

    // Los selects de fila muestran "Operativo"; el filtro muestra "Todos los estados"
    const [selectFila] = screen.getAllByDisplayValue("Operativo");
    await user.selectOptions(selectFila, "mantenimiento");

    expect(await screen.findByText("mantenimiento")).toBeInTheDocument();
  });

  it("elimina un bus tras confirmar", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    server.use(
      http.delete(`${API}/api/buses/ABC-123`, () => new HttpResponse(null, { status: 204 })),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("ABC-123");

    await user.click(screen.getAllByRole("button", { name: "Eliminar" })[0]);

    await vi.waitFor(() =>
      expect(screen.queryByText("ABC-123")).not.toBeInTheDocument(),
    );
    expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining("ABC-123"));
    expect(screen.getByText("1 buses en total")).toBeInTheDocument();
  });

  it("no elimina si el usuario cancela la confirmación", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const user = userEvent.setup();
    setup();
    await screen.findByText("ABC-123");

    await user.click(screen.getAllByRole("button", { name: "Eliminar" })[0]);

    expect(screen.getByText("ABC-123")).toBeInTheDocument();
  });

  it("supervisor solo gestiona los buses de su área", async () => {
    setup(SUPERVISOR);
    await screen.findByText("ABC-123");
    // Solo el bus del área 1 tiene acciones de gestión
    expect(screen.getAllByRole("button", { name: "Eliminar" })).toHaveLength(1);
  });
});
