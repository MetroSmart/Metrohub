import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Usuarios from "../../pages/Usuarios.jsx";

// El nombre no debe coincidir con ningún usuario de la tabla: el Sidebar lo
// renderiza de inmediato y los findByText resolverían antes de cargar la tabla
const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const API = "http://localhost:8000";

const mockUsuarios = [
  { id: 1, nombre: "Ana", apellidos: "Torres", email: "ana@metrohub.gob.pe", dni: "11111111", rol: "admin_atu", area_id: null, activo: true },
  { id: 2, nombre: "Luis", apellidos: "Gómez", email: "luis@metrohub.gob.pe", dni: "22222222", rol: "supervisor_area", area_id: 1, activo: true },
];

let rolesPedidos;

beforeEach(() => {
  rolesPedidos = [];
  server.use(
    http.get(`${API}/api/usuarios`, ({ request }) => {
      rolesPedidos.push(new URL(request.url).searchParams.get("rol"));
      return HttpResponse.json({ total: mockUsuarios.length, usuarios: mockUsuarios });
    }),
  );
});

function setup() {
  return render(<Usuarios user={ADMIN} onNav={() => {}} onLogout={() => {}} />);
}

describe("Usuarios (RF01 — administración)", () => {
  it("lista los usuarios con email, DNI, área y estado", async () => {
    setup();
    expect(await screen.findByText("Ana Torres")).toBeInTheDocument();
    expect(screen.getByText("Luis Gómez")).toBeInTheDocument();
    expect(screen.getByText("ana@metrohub.gob.pe")).toBeInTheDocument();
    expect(screen.getByText("22222222")).toBeInTheDocument();
    expect(await screen.findByText("Op. Norte")).toBeInTheDocument(); // área del supervisor
    expect(screen.getByText("—")).toBeInTheDocument();                // admin sin área
    expect(screen.getAllByText("Activo")).toHaveLength(2);
    expect(screen.getByText("2 usuarios")).toBeInTheDocument();
  });

  it("filtra por rol consultando al API", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.selectOptions(screen.getByDisplayValue("Todos los roles"), "admin_atu");

    await vi.waitFor(() => expect(rolesPedidos).toContain("admin_atu"));
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/usuarios`, () =>
        HttpResponse.json({ detail: "Sin permisos" }, { status: 403 }),
      ),
    );
    setup();
    expect(await screen.findByText(/error al cargar: sin permisos/i)).toBeInTheDocument();
  });

  it("valida los campos obligatorios al crear", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.click(screen.getByRole("button", { name: "+ Nuevo usuario" }));
    await user.click(screen.getByRole("button", { name: "Crear usuario" }));

    expect(await screen.findByText('El campo "email" es obligatorio.')).toBeInTheDocument();
  });

  it("exige área cuando el rol es supervisor", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.click(screen.getByRole("button", { name: "+ Nuevo usuario" }));
    await user.type(screen.getByPlaceholderText("Carlos"), "Pedro");
    await user.type(screen.getByPlaceholderText("Ramírez Torres"), "Salas Vega");
    await user.type(screen.getByPlaceholderText("usuario@metrohub.gob.pe"), "pedro@metrohub.gob.pe");
    await user.type(screen.getByPlaceholderText("12345678"), "33333333");
    await user.type(screen.getByPlaceholderText("Mínimo 6 caracteres"), "secreta1");
    await user.click(screen.getByRole("button", { name: "Crear usuario" }));

    expect(
      await screen.findByText("El supervisor debe tener un área asignado."),
    ).toBeInTheDocument();
  });

  it("crea un supervisor con su área y lo agrega a la tabla", async () => {
    let body;
    server.use(
      http.post(`${API}/api/usuarios`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 3, ...body, activo: true }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.click(screen.getByRole("button", { name: "+ Nuevo usuario" }));
    await user.type(screen.getByPlaceholderText("Carlos"), "Pedro");
    await user.type(screen.getByPlaceholderText("Ramírez Torres"), "Salas Vega");
    await user.type(screen.getByPlaceholderText("usuario@metrohub.gob.pe"), "pedro@metrohub.gob.pe");
    await user.type(screen.getByPlaceholderText("12345678"), "33333333");
    await user.type(screen.getByPlaceholderText("Mínimo 6 caracteres"), "secreta1");
    await user.selectOptions(screen.getByDisplayValue("— Seleccionar —"), "1");
    await user.click(screen.getByRole("button", { name: "Crear usuario" }));

    expect(await screen.findByText("Pedro Salas Vega")).toBeInTheDocument();
    expect(screen.getByText("3 usuarios")).toBeInTheDocument();
    expect(body).toEqual({
      email: "pedro@metrohub.gob.pe", password: "secreta1",
      nombre: "Pedro", apellidos: "Salas Vega", dni: "33333333",
      rol: "supervisor_area", area_id: 1,
    });
  });

  it("desactiva un usuario con el toggle", async () => {
    server.use(
      http.patch(`${API}/api/usuarios/1`, async ({ request }) => {
        const { activo } = await request.json();
        return HttpResponse.json({ id: 1, activo });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.click(screen.getAllByRole("button", { name: "Desactivar" })[0]);

    expect(await screen.findByText("Inactivo")).toBeInTheDocument();
  });

  it("cambia la contraseña de un usuario validando el mínimo", async () => {
    let body;
    server.use(
      http.patch(`${API}/api/usuarios/1/password`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ ok: true });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Ana Torres");

    await user.click(screen.getAllByRole("button", { name: "Contraseña" })[0]);
    expect(screen.getByText("Cambiar contraseña")).toBeInTheDocument();

    // Demasiado corta
    await user.type(screen.getByPlaceholderText("Mínimo 6 caracteres"), "abc");
    await user.click(screen.getByRole("button", { name: "Cambiar" }));
    expect(
      await screen.findByText("La contraseña debe tener al menos 6 caracteres."),
    ).toBeInTheDocument();

    // Válida: guarda y cierra el modal
    await user.type(screen.getByPlaceholderText("Mínimo 6 caracteres"), "nueva123");
    await user.click(screen.getByRole("button", { name: "Cambiar" }));

    await vi.waitFor(() =>
      expect(screen.queryByText("Cambiar contraseña")).not.toBeInTheDocument(),
    );
    expect(body).toEqual({ nueva_password: "abcnueva123" });
  });
});
