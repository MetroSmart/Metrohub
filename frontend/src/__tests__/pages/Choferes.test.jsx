import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Choferes from "../../pages/Choferes.jsx";

const ADMIN = { role: "admin_atu", name: "Root Metrohub" };
const SUPERVISOR = { role: "supervisor_area", name: "Sup Norte", area_id: 1 };
const API = "http://localhost:8000";

const isoOffset = (dias) => {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return d.toISOString().slice(0, 10);
};

// Juan: documentos vigentes (>30d). Rosa: licencia por vencer y certificado vencido.
const CHOFERES = [
  {
    id: 7, nombres: "Juan", apellidos: "Pérez García", dni: "44444444",
    numero_licencia: "Q11111111", tipo_licencia: "A-IIIA", estado: "activo",
    area_id: 1, fec_vence_licencia: isoOffset(200), fec_vence_certif_prot: isoOffset(200),
  },
  {
    id: 9, nombres: "Rosa", apellidos: "Quispe Mamani", dni: "55555555",
    numero_licencia: "Q22222222", tipo_licencia: "A-IIIB", estado: "suspendido",
    area_id: 2, fec_vence_licencia: isoOffset(10), fec_vence_certif_prot: isoOffset(-5),
  },
];

let queriesPedidas;

beforeEach(() => {
  queriesPedidas = [];
  server.use(
    http.get(`${API}/api/choferes`, ({ request }) => {
      queriesPedidas.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(CHOFERES);
    }),
    http.get(`${API}/api/disponibilidad`, () =>
      HttpResponse.json({
        total: 1,
        disponibilidades: [{
          id: 31, chofer_id: 7, fecha: "2026-06-15",
          hora_desde: "08:00", hora_hasta: "12:00",
          motivo: "medico", observaciones: null,
        }],
      }),
    ),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

function setup(user = ADMIN) {
  return render(<Choferes user={user} onNav={() => {}} onLogout={() => {}} />);
}

describe("Choferes (RF03)", () => {
  it("lista los choferes con licencia y alertas de vencimiento", async () => {
    setup();
    expect(await screen.findByText("Juan Pérez García")).toBeInTheDocument();
    expect(screen.getByText("Rosa Quispe Mamani")).toBeInTheDocument();
    expect(screen.getByText("Q11111111")).toBeInTheDocument();
    expect(screen.getByText("A-IIIB")).toBeInTheDocument();
    // Certificado de Rosa vencido hace 5 días y licencia por vencer en ~10 días
    expect(screen.getByText("VENCIDA")).toBeInTheDocument();
    expect(screen.getByText(/^\d+d$/)).toBeInTheDocument();
    expect(screen.getByText("2 choferes")).toBeInTheDocument();
  });

  it("supervisor consulta solo su área y no puede editar el estado", async () => {
    setup(SUPERVISOR);
    expect(await screen.findByText("Juan Pérez García")).toBeInTheDocument();
    expect(queriesPedidas[0]).toMatchObject({ area_id: "1" });
    // Sin selects de estado por fila: el estado se muestra como texto en un span
    // ("suspendido" también existe como opción del filtro, por eso getAllByText)
    expect(screen.getAllByText("suspendido").some(el => el.tagName === "SPAN")).toBe(true);
    expect(screen.queryByDisplayValue("activo")).not.toBeInTheDocument();
  });

  it("filtra por estado consultando al API", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Juan Pérez García");

    await user.selectOptions(screen.getByDisplayValue("Todos los estados"), "suspendido");

    await vi.waitFor(() =>
      expect(queriesPedidas.some(q => q.estado === "suspendido")).toBe(true),
    );
  });

  it("admin cambia el estado de un chofer desde la fila", async () => {
    server.use(
      http.patch(`${API}/api/choferes/7/estado`, async ({ request }) => {
        const { estado } = await request.json();
        return HttpResponse.json({ id: 7, estado });
      }),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Juan Pérez García");

    await user.selectOptions(screen.getByDisplayValue("activo"), "vacaciones");

    expect(await screen.findByDisplayValue("vacaciones")).toBeInTheDocument();
  });

  it("muestra el error cuando la carga falla", async () => {
    server.use(
      http.get(`${API}/api/choferes`, () =>
        HttpResponse.json({ detail: "Sin permisos" }, { status: 403 }),
      ),
    );
    setup();
    expect(await screen.findByText(/error al cargar: sin permisos/i)).toBeInTheDocument();
  });

  it("valida los campos obligatorios al registrar un chofer", async () => {
    const user = userEvent.setup();
    setup();
    await screen.findByText("Juan Pérez García");

    await user.click(screen.getByRole("button", { name: "+ Registrar chofer" }));
    await user.click(screen.getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText('El campo "dni" es obligatorio.')).toBeInTheDocument();
  });

  it("registra un chofer y avisa el acceso al portal", async () => {
    vi.spyOn(window, "alert").mockImplementation(() => {});
    let body;
    server.use(
      http.post(`${API}/api/choferes`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({
          id: 10, ...body, estado: "activo",
          acceso_portal: { email: "33333333@metrohub.gob.pe" },
        }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    const { baseElement } = setup();
    await screen.findByText("Juan Pérez García");

    await user.click(screen.getByRole("button", { name: "+ Registrar chofer" }));
    await user.type(screen.getByPlaceholderText("Carlos Alberto"), "Pedro");
    await user.type(screen.getByPlaceholderText("Ramírez Torres"), "Salas Vega");
    await user.type(screen.getByPlaceholderText("12345678"), "33333333");
    await user.type(screen.getByPlaceholderText("Q12345678"), "Q33333333");
    await user.selectOptions(screen.getByDisplayValue("— Seleccionar —"), "1");

    // Inputs de fecha del modal en orden: nacimiento, vence licencia, vence certificado
    const fechas = baseElement.querySelectorAll('input[type="date"]');
    fireEvent.change(fechas[0], { target: { value: "1990-04-12" } });
    fireEvent.change(fechas[1], { target: { value: isoOffset(300) } });
    fireEvent.change(fechas[2], { target: { value: isoOffset(300) } });

    await user.click(screen.getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText("Pedro Salas Vega")).toBeInTheDocument();
    expect(screen.getByText("3 choferes")).toBeInTheDocument();
    expect(body).toMatchObject({ dni: "33333333", area_id: 1, tipo_licencia: "A-IIIA" });
    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining("33333333@metrohub.gob.pe"));
  });

  it("la pestaña Indisponibilidades lista los registros y permite eliminar", async () => {
    server.use(
      http.delete(`${API}/api/disponibilidad/31`, () => new HttpResponse(null, { status: 204 })),
    );
    const user = userEvent.setup();
    setup();
    await screen.findByText("Juan Pérez García");

    await user.click(screen.getByRole("button", { name: "Indisponibilidades" }));

    expect(await screen.findByText("medico")).toBeInTheDocument();
    expect(screen.getByText("2026-06-15")).toBeInTheDocument();
    expect(screen.getByText("1 registros")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Eliminar" }));

    expect(await screen.findByText("Sin registros de indisponibilidad.")).toBeInTheDocument();
  });

  it("registra una indisponibilidad para un chofer activo", async () => {
    let body;
    server.use(
      http.post(`${API}/api/disponibilidad`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ id: 32, ...body }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    const { baseElement } = setup();
    await screen.findByText("Juan Pérez García");

    await user.click(screen.getByRole("button", { name: "Indisponibilidades" }));
    await user.click(screen.getByRole("button", { name: "+ Registrar indisponibilidad" }));

    // Validación con campos vacíos
    await user.click(screen.getByRole("button", { name: "Registrar" }));
    expect(
      await screen.findByText("Chofer, fecha, hora desde y hora hasta son obligatorios."),
    ).toBeInTheDocument();

    // Solo los choferes activos aparecen en el selector (Rosa está suspendida)
    const selectorChofer = screen.getByDisplayValue("— Seleccionar —");
    expect([...selectorChofer.options].map(o => o.textContent)).toEqual([
      "— Seleccionar —", "Juan Pérez García",
    ]);

    await user.selectOptions(selectorChofer, "7");
    fireEvent.change(baseElement.querySelector('input[type="date"]'), {
      target: { value: "2026-06-20" },
    });
    await user.click(screen.getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText("2026-06-20")).toBeInTheDocument();
    expect(screen.getByText("2 registros")).toBeInTheDocument();
    expect(body).toEqual({
      chofer_id: 7, fecha: "2026-06-20", hora_desde: "08:00",
      hora_hasta: "18:00", motivo: "descanso", observaciones: null,
    });
  });
});
