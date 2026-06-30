import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Areas from "../../pages/Areas.jsx";

const ADMIN = { role: "admin_atu", name: "Ana Torres" };
const API = "http://localhost:8000";

function setup() {
  return render(<Areas user={ADMIN} onNav={() => {}} onLogout={() => {}} />);
}

describe("Areas (RF08)", () => {
  it("lista las áreas operativas con su estado", async () => {
    setup();
    expect(await screen.findByText("Operaciones Norte")).toBeInTheDocument();
    expect(screen.getByText("Operaciones Sur")).toBeInTheDocument();
    expect(screen.getByText("Op. Norte")).toBeInTheDocument();
    expect(screen.getAllByText("Activa")).toHaveLength(2);
    expect(screen.getByText("2 áreas operativas")).toBeInTheDocument();
  });

  it("muestra el mensaje vacío cuando no hay áreas", async () => {
    server.use(
      http.get(`${API}/api/areas`, () => HttpResponse.json({ total: 0, areas: [] })),
    );
    setup();
    expect(await screen.findByText("Sin áreas operativas registradas.")).toBeInTheDocument();
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/areas`, () =>
        HttpResponse.json({ detail: "Sin permisos" }, { status: 403 }),
      ),
    );
    setup();
    expect(await screen.findByText(/error al cargar: sin permisos/i)).toBeInTheDocument();
  });

  it("valida campos obligatorios al crear", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Operaciones Norte");

    await user.click(screen.getByRole("button", { name: "+ Nueva área" }));
    await user.click(screen.getByRole("button", { name: "Crear" }));

    expect(
      await screen.findByText("Nombre y nombre corto son obligatorios."),
    ).toBeInTheDocument();
  });

  it("crea un área y la agrega a la tabla", async () => {
    let body;
    server.use(
      http.post(`${API}/api/areas`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 3, ...body, activo: true }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Operaciones Norte");

    await user.click(screen.getByRole("button", { name: "+ Nueva área" }));
    await user.type(screen.getByPlaceholderText("Ej. Operaciones Norte"), "Operaciones Este");
    await user.type(screen.getByPlaceholderText("Ej. Op. Norte"), "Op. Este");
    await user.click(screen.getByRole("button", { name: "Crear" }));

    expect(await screen.findByText("Operaciones Este")).toBeInTheDocument();
    expect(screen.getByText("3 áreas operativas")).toBeInTheDocument();
    // El modal se cierra tras crear
    expect(screen.queryByText("Nueva área operativa")).not.toBeInTheDocument();
    expect(body).toEqual({ nombre: "Operaciones Este", nombre_corto: "Op. Este", descripcion: null });
  });

  it("muestra el error del backend si la creación falla", async () => {
    server.use(
      http.post(`${API}/api/areas`, () =>
        HttpResponse.json({ detail: "Ya existe un área con ese nombre" }, { status: 409 }),
      ),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Operaciones Norte");

    await user.click(screen.getByRole("button", { name: "+ Nueva área" }));
    await user.type(screen.getByPlaceholderText("Ej. Operaciones Norte"), "Operaciones Norte");
    await user.type(screen.getByPlaceholderText("Ej. Op. Norte"), "Op. Norte");
    await user.click(screen.getByRole("button", { name: "Crear" }));

    expect(await screen.findByText("Ya existe un área con ese nombre")).toBeInTheDocument();
    // El modal sigue abierto
    expect(screen.getByText("Nueva área operativa")).toBeInTheDocument();
  });

  it("desactiva un área con el toggle", async () => {
    server.use(
      http.patch(`${API}/api/areas/1`, async ({ request }) => {
        const { activo } = await request.json();
        return HttpResponse.json({ id: 1, activo });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Operaciones Norte");

    await user.click(screen.getAllByRole("button", { name: "Desactivar" })[0]);

    expect(await screen.findByText("Inactiva")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Activar" })).toBeInTheDocument();
  });
});
