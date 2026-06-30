import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Rutas from "../../pages/Rutas.jsx";

const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const SUPERVISOR = { role: "supervisor_area", name: "Sup Norte", area_id: 1 };
const API = "http://localhost:8000";

function setup(user = ADMIN) {
  return render(<Rutas user={user} onNav={() => {}} onLogout={() => {}} />);
}

describe("Rutas (RF02)", () => {
  it("lista las rutas con tipo, horario y frecuencia", async () => {
    setup();
    expect(await screen.findByText("SIT-1")).toBeInTheDocument();
    expect(screen.getByText("Naranjal - Matellini")).toBeInTheDocument();
    expect(screen.getByText("regular")).toBeInTheDocument();
    expect(screen.getByText("nocturna")).toBeInTheDocument();
    expect(screen.getByText("05:00 – 23:00")).toBeInTheDocument();
    expect(screen.getByText("Cada 10 min")).toBeInTheDocument();
    expect(screen.getByText("Activa")).toBeInTheDocument();
    expect(screen.getByText("Inactiva")).toBeInTheDocument();
    expect(screen.getByText("2 rutas en total")).toBeInTheDocument();
  });

  it("la pestaña Estaciones lista el catálogo", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getByRole("button", { name: "Estaciones" }));

    expect(await screen.findByText("EST-001")).toBeInTheDocument();
    expect(screen.getByText("Estación Naranjal")).toBeInTheDocument();
    expect(screen.getByText("terminal")).toBeInTheDocument();
    expect(screen.getByText("transferencia")).toBeInTheDocument();
    expect(screen.getByText("2 estaciones en total")).toBeInTheDocument();
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/rutas`, () =>
        HttpResponse.json({ detail: "Servicio caído" }, { status: 500 }),
      ),
    );
    setup();
    expect(await screen.findByText(/error al cargar: servicio caído/i)).toBeInTheDocument();
  });

  it("supervisor no ve acciones de administración", async () => {
    setup(SUPERVISOR);
    await screen.findByText("SIT-1");
    expect(screen.queryByRole("button", { name: "+ Nueva ruta" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
    // El estado es un span, no un botón de toggle
    expect(screen.queryByRole("button", { name: "Activa" })).not.toBeInTheDocument();
  });

  it("crea una ruta validando código y nombre", async () => {
    let body;
    server.use(
      http.post(`${API}/api/rutas`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 3, ...body, activa: true }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getByRole("button", { name: "+ Nueva ruta" }));
    await user.click(screen.getByRole("button", { name: "Crear ruta" }));
    expect(await screen.findByText("Código y nombre son obligatorios.")).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("ej. SIT-1"), "EXP-2");
    await user.type(screen.getByPlaceholderText("ej. Naranjal - Matellini"), "Expreso Sur");
    await user.click(screen.getByRole("button", { name: "Crear ruta" }));

    expect(await screen.findByText("EXP-2")).toBeInTheDocument();
    expect(screen.getByText("3 rutas en total")).toBeInTheDocument();
    expect(body).toMatchObject({ codigo: "EXP-2", nombre: "Expreso Sur", tipo: "regular", frecuencia_min: 10 });
  });

  it("edita una ruta existente con el código bloqueado", async () => {
    let body;
    server.use(
      http.put(`${API}/api/rutas/1`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({
          id: 1, ...body, activa: true,
        });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getAllByRole("button", { name: "Editar" })[0]);
    expect(screen.getByText("Editar ruta — SIT-1")).toBeInTheDocument();
    expect(screen.getByDisplayValue("SIT-1")).toBeDisabled();

    const nombre = screen.getByDisplayValue("Naranjal - Matellini");
    await user.clear(nombre);
    await user.type(nombre, "Naranjal Express");
    await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(await screen.findByText("Naranjal Express")).toBeInTheDocument();
    expect(screen.queryByText("Naranjal - Matellini")).not.toBeInTheDocument();
    expect(body).toMatchObject({ codigo: "SIT-1", nombre: "Naranjal Express" });
  });

  it("activa/desactiva una ruta con el toggle de estado", async () => {
    server.use(
      http.patch(`${API}/api/rutas/1/estado`, ({ request }) => {
        const activa = new URL(request.url).searchParams.get("activa") === "true";
        return HttpResponse.json({ ruta: { id: 1, activa } });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getByRole("button", { name: "Activa" }));

    // SIT-1 pasa a Inactiva; junto con N-205 ya inactiva, hay dos
    await screen.findAllByText("Inactiva");
    expect(screen.getAllByText("Inactiva")).toHaveLength(2);
    expect(screen.queryByText("Activa")).not.toBeInTheDocument();
  });

  it("gestiona el recorrido: asigna y quita estaciones", async () => {
    const RECORRIDO = [{
      estacion_id: 1, orden: 1, codigo: "EST-001",
      nombre: "Estación Naranjal", tramo: "norte", tiempo_est_min: null,
    }];
    let bodyAsig;
    server.use(
      http.get(`${API}/api/rutas/1/estaciones`, () => HttpResponse.json(RECORRIDO)),
      http.post(`${API}/api/rutas/1/estaciones`, async ({ request }) => {
        bodyAsig = await request.json();
        return HttpResponse.json([
          ...RECORRIDO,
          { estacion_id: 2, orden: 2, codigo: "EST-014", nombre: "Estación Central", tramo: "centro", tiempo_est_min: 12 },
        ]);
      }),
      http.delete(`${API}/api/rutas/1/estaciones/1`, () => new HttpResponse(null, { status: 204 })),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getAllByRole("button", { name: "Recorrido" })[0]);
    expect(await screen.findByText("Recorrido — SIT-1")).toBeInTheDocument();
    expect(await screen.findByText("Estación Naranjal")).toBeInTheDocument();

    // Validación del formulario de asignación
    await user.click(screen.getByRole("button", { name: "Agregar" }));
    expect(await screen.findByText("Estación y orden son obligatorios.")).toBeInTheDocument();

    // Asigna la estación central en orden 2
    await user.selectOptions(screen.getByDisplayValue("— Seleccionar —"), "2");
    await user.type(screen.getByPlaceholderText("1"), "2");
    await user.click(screen.getByRole("button", { name: "Agregar" }));

    expect(await screen.findByText("Estación Central")).toBeInTheDocument();
    expect(screen.getByText("12 min")).toBeInTheDocument();
    expect(bodyAsig).toEqual({ estacion_id: 2, orden: 2, tiempo_est_min: null });

    // Quita la primera estación del recorrido
    await user.click(screen.getAllByRole("button", { name: "Quitar" })[0]);
    await screen.findByText("Estación Central");
    expect(screen.queryByText("Estación Naranjal")).not.toBeInTheDocument();
  });

  it("crea una estación desde la pestaña Estaciones", async () => {
    let body;
    server.use(
      http.post(`${API}/api/estaciones`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 9, ...body, activa: true }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("SIT-1");

    await user.click(screen.getByRole("button", { name: "Estaciones" }));
    await user.click(screen.getByRole("button", { name: "+ Nueva estación" }));

    await user.click(screen.getByRole("button", { name: "Crear estación" }));
    expect(await screen.findByText("Código y nombre son obligatorios.")).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("Ej. EST-001"), "EST-099");
    await user.type(screen.getByPlaceholderText("Ej. Estación Naranjal"), "Estación Sur");
    await user.click(screen.getByRole("button", { name: "Crear estación" }));

    expect(await screen.findByText("EST-099")).toBeInTheDocument();
    expect(screen.getByText("3 estaciones en total")).toBeInTheDocument();
    expect(body).toMatchObject({
      codigo: "EST-099", nombre: "Estación Sur", tipo: "intermedia",
      tramo: "norte", orden_troncal: null, latitud: null, longitud: null,
    });
  });
});
