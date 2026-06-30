import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Sidebar from "../../components/Sidebar.jsx";

const ADMIN = { role: "admin_atu", name: "Ana Torres" };
const SUPERVISOR = { role: "supervisor_area", name: "Supervisor Norte", area_id: 1 };
const CHOFER = { role: "chofer", name: "Juan Pérez" };

describe("Sidebar (UI por rol)", () => {
  it("admin ve Principal, Reportes y Administración", () => {
    render(<Sidebar active="dashboard" onNav={() => {}} onLogout={() => {}} user={ADMIN} />);
    for (const item of ["Dashboard", "Rutas y Estaciones", "Programación", "Choferes", "Flota"]) {
      expect(screen.getByText(item)).toBeInTheDocument();
    }
    expect(screen.getByText("Exportar PDF/XLSX")).toBeInTheDocument();
    expect(screen.getByText("Administración")).toBeInTheDocument();
    expect(screen.getByText("Usuarios")).toBeInTheDocument();
    expect(screen.getByText("Áreas Operativas")).toBeInTheDocument();
    expect(screen.getByText("Admin ATU")).toBeInTheDocument();
  });

  it("supervisor no ve la sección Administración", () => {
    render(<Sidebar active="dashboard" onNav={() => {}} onLogout={() => {}} user={SUPERVISOR} />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Exportar PDF/XLSX")).toBeInTheDocument();
    expect(screen.queryByText("Administración")).not.toBeInTheDocument();
    expect(screen.queryByText("Usuarios")).not.toBeInTheDocument();
    expect(screen.queryByText("Áreas Operativas")).not.toBeInTheDocument();
    expect(screen.getByText("Supervisor")).toBeInTheDocument();
  });

  it("chofer solo ve su jornada con Mis rutas asignadas", () => {
    render(<Sidebar active="mis-rutas" onNav={() => {}} onLogout={() => {}} user={CHOFER} />);
    expect(screen.getByText("Mi jornada")).toBeInTheDocument();
    expect(screen.getByText("Mis rutas asignadas")).toBeInTheDocument();
    expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
    expect(screen.queryByText("Flota")).not.toBeInTheDocument();
    expect(screen.queryByText("Exportar PDF/XLSX")).not.toBeInTheDocument();
    expect(screen.getByText("Chofer")).toBeInTheDocument();
  });

  it("clic en un ítem llama onNav con su key", async () => {
    const user = userEvent.setup();
    const onNav = vi.fn();
    render(<Sidebar active="dashboard" onNav={onNav} onLogout={() => {}} user={ADMIN} />);

    await user.click(screen.getByText("Rutas y Estaciones"));
    expect(onNav).toHaveBeenCalledWith("rutas");

    await user.click(screen.getByText("Flota"));
    expect(onNav).toHaveBeenCalledWith("buses");
  });

  it("Cerrar sesión llama onLogout", async () => {
    const user = userEvent.setup();
    const onLogout = vi.fn();
    render(<Sidebar active="dashboard" onNav={() => {}} onLogout={onLogout} user={ADMIN} />);

    await user.click(screen.getByText(/cerrar sesión/i));
    expect(onLogout).toHaveBeenCalledTimes(1);
  });

  it("muestra el nombre del usuario y su inicial en el avatar", () => {
    render(<Sidebar active="dashboard" onNav={() => {}} onLogout={() => {}} user={CHOFER} />);
    expect(screen.getByText("Juan Pérez")).toBeInTheDocument();
    expect(screen.getByText("J")).toBeInTheDocument();
  });

  it("sin usuario muestra placeholder", () => {
    render(<Sidebar active="dashboard" onNav={() => {}} onLogout={() => {}} user={null} />);
    expect(screen.getByText("Usuario")).toBeInTheDocument();
    expect(screen.getByText("U")).toBeInTheDocument();
  });
});
