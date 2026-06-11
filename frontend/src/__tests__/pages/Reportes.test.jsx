import { describe, it, expect, vi, beforeAll, afterAll } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Reportes from "../../pages/Reportes.jsx";

const ADMIN = { role: "admin_atu", name: "Ana Torres" };
const SUPERVISOR = { role: "supervisor_area", name: "Supervisor Norte" };
const API = "http://localhost:8000";

// jsdom no implementa descargas: stub de blob URL y del click del <a>
beforeAll(() => {
  URL.createObjectURL = vi.fn(() => "blob:fake");
  URL.revokeObjectURL = vi.fn();
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
});

afterAll(() => {
  vi.restoreAllMocks();
});

describe("Reportes (RF07)", () => {
  it("admin ve las tarjetas de exportación PDF y XLSX", () => {
    render(<Reportes user={ADMIN} onNav={() => {}} onLogout={() => {}} />);
    expect(screen.getByText("Reporte PDF")).toBeInTheDocument();
    expect(screen.getByText("Reporte XLSX")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Descargar PDF" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Descargar XLSX" })).toBeInTheDocument();
  });

  it("supervisor no puede exportar y ve el aviso", () => {
    render(<Reportes user={SUPERVISOR} onNav={() => {}} onLogout={() => {}} />);
    expect(
      screen.getByText(/solo el administrador atu puede generar y exportar/i),
    ).toBeInTheDocument();
    expect(screen.queryByText("Reporte PDF")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /descargar/i })).not.toBeInTheDocument();
  });

  it("exporta el PDF y muestra confirmación", async () => {
    let body;
    server.use(
      http.post(`${API}/api/reportes/exportar`, async ({ request }) => {
        body = await request.json();
        return new HttpResponse("PDFDATA", {
          status: 200,
          headers: { "Content-Type": "application/pdf" },
        });
      }),
    );
    const user = userEvent.setup();
    render(<Reportes user={ADMIN} onNav={() => {}} onLogout={() => {}} />);

    await user.click(screen.getByRole("button", { name: "Descargar PDF" }));

    expect(
      await screen.findByText("Reporte PDF descargado correctamente."),
    ).toBeInTheDocument();
    expect(body).toEqual({ formato: "pdf", usar_familia_atu: true });
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it("exporta el XLSX y muestra confirmación", async () => {
    server.use(
      http.post(`${API}/api/reportes/exportar`, () =>
        new HttpResponse("XLSXDATA", { status: 200 }),
      ),
    );
    const user = userEvent.setup();
    render(<Reportes user={ADMIN} onNav={() => {}} onLogout={() => {}} />);

    await user.click(screen.getByRole("button", { name: "Descargar XLSX" }));

    expect(
      await screen.findByText("Reporte XLSX descargado correctamente."),
    ).toBeInTheDocument();
  });

  it("muestra el detail del backend cuando la exportación falla", async () => {
    server.use(
      http.post(`${API}/api/reportes/exportar`, () =>
        HttpResponse.json({ detail: "No hay datos para el reporte" }, { status: 422 }),
      ),
    );
    const user = userEvent.setup();
    render(<Reportes user={ADMIN} onNav={() => {}} onLogout={() => {}} />);

    await user.click(screen.getByRole("button", { name: "Descargar PDF" }));

    expect(await screen.findByText("No hay datos para el reporte")).toBeInTheDocument();
  });
});
