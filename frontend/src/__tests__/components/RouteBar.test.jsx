import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import RouteBar from "../../components/RouteBar.jsx";

describe("RouteBar (RF02)", () => {
  it("muestra código, nombre y tipo de la ruta", () => {
    render(<RouteBar code="CR-01" name="Corredor Rojo Troncal" tipo="regular" />);
    expect(screen.getByText("CR-01")).toBeInTheDocument();
    expect(screen.getByText("Corredor Rojo Troncal")).toBeInTheDocument();
    expect(screen.getByText("regular")).toBeInTheDocument();
  });

  it("colorea el badge según el tipo", () => {
    render(<RouteBar code="CA-02" name="Expreso Javier Prado" tipo="expreso" />);
    const badge = screen.getByText("expreso");
    expect(badge.style.background).toBe("rgb(234, 243, 222)"); // #EAF3DE
    expect(badge.style.color).toBe("rgb(39, 80, 10)");         // #27500A
  });

  it("usa el estilo de fallback para un tipo desconocido", () => {
    render(<RouteBar code="CX-09" name="Ruta especial" tipo="especial" />);
    const badge = screen.getByText("especial");
    expect(badge.style.background).toBe("rgb(240, 240, 240)"); // #f0f0f0
    expect(badge.style.color).toBe("rgb(68, 68, 68)");         // #444
  });

  it("muestra un guion cuando no hay tipo", () => {
    render(<RouteBar code="CN-03" name="Ruta sin tipo" tipo={null} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
