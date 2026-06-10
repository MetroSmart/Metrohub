import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import KpiCard from "../../components/KpiCard.jsx";

describe("KpiCard", () => {
  it("renderiza label y value", () => {
    render(<KpiCard label="Rutas activas" value={12} />);
    expect(screen.getByText("Rutas activas")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("renderiza el sub cuando se provee", () => {
    render(<KpiCard label="Choferes" value={45} sub="+3 vs ayer" tone="good" />);
    expect(screen.getByText("+3 vs ayer")).toBeInTheDocument();
  });

  it("omite el sub cuando no se provee", () => {
    const { container } = render(<KpiCard label="Buses" value={20} />);
    expect(container.textContent).not.toContain("undefined");
  });

  it("aplica el color del tone correctamente", () => {
    render(<KpiCard label="Conflictos" value={3} sub="pendientes" tone="danger" />);
    const sub = screen.getByText("pendientes");
    expect(sub).toHaveStyle({ color: "#A32D2D" });
  });

  it("usa color neutral por defecto", () => {
    render(<KpiCard label="X" value={1} sub="info" />);
    expect(screen.getByText("info")).toHaveStyle({ color: "#888" });
  });
});
