import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import { mockKpis } from "../../test/handlers.js";
import Dashboard from "../../pages/Dashboard.jsx";

const ADMIN = { role: "admin_atu", name: "Ana Torres" };
const SUPERVISOR = { role: "supervisor_area", name: "Supervisor Norte" };

function setup(user = ADMIN) {
  const onNav = vi.fn();
  render(<Dashboard user={user} onNav={onNav} onLogout={() => {}} />);
  return { onNav };
}

describe("Dashboard (RF05/RF06)", () => {
  it("muestra los KPIs que devuelve el API", async () => {
    setup();
    expect(await screen.findByText(String(mockKpis.rutas_activas))).toBeInTheDocument();
    expect(screen.getByText(String(mockKpis.choferes_activos))).toBeInTheDocument();
    expect(screen.getByText("en operación hoy")).toBeInTheDocument();
    expect(screen.getByText(`${mockKpis.buses_operativos} buses operativos`)).toBeInTheDocument();
    expect(screen.getByText("Conflictos abiertos")).toBeInTheDocument();
    expect(screen.getByText("Certif. por vencer")).toBeInTheDocument();
  });

  it("lista solo las rutas activas", async () => {
    setup();
    expect(await screen.findByText("SIT-1")).toBeInTheDocument();
    expect(screen.getByText("Naranjal - Matellini")).toBeInTheDocument();
    // N-205 está inactiva: el dashboard pide solo_activas=true
    expect(screen.queryByText("N-205")).not.toBeInTheDocument();
  });

  it("muestra las alertas de documentos de choferes", async () => {
    setup();
    expect(
      await screen.findByText("Certif. VENCIDA — Juan Pérez García (0d)"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Certif. por vencer — Rosa Quispe Mamani (12d)"),
    ).toBeInTheDocument();
  });

  it("muestra la alerta informativa cuando no hay documentos por vencer", async () => {
    server.use(
      http.get("http://localhost:8000/api/choferes/alertas/documentos", () =>
        HttpResponse.json({ total: 0, choferes: [] }),
      ),
    );
    setup();
    expect(await screen.findByText("Sin alertas de documentos")).toBeInTheDocument();
  });

  it("muestra el badge según el rol", async () => {
    setup(SUPERVISOR);
    expect(await screen.findByText("Dashboard operativo")).toBeInTheDocument();
    // "Supervisor" aparece en el Sidebar y en el badge del topbar
    expect(screen.getAllByText("Supervisor").length).toBeGreaterThanOrEqual(2);
  });

  it("los accesos rápidos navegan a grilla, choferes y rutas", async () => {
    const user = userEvent.setup();
    const { onNav } = setup();

    await user.click(screen.getByText(/ver grilla de horarios/i));
    expect(onNav).toHaveBeenCalledWith("grilla");
    await user.click(screen.getByText(/ver choferes/i));
    expect(onNav).toHaveBeenCalledWith("choferes");
    await user.click(screen.getByText(/ver rutas/i));
    expect(onNav).toHaveBeenCalledWith("rutas");
  });
});
