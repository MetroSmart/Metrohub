import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import AlertPanel from "../../components/AlertPanel.jsx";

const ALERTAS = [
  { type: "danger", text: "Certif. VENCIDA — Juan Pérez García (0d)", time: "vence 2026-06-01" },
  { type: "warn", text: "Certif. por vencer — Rosa Quispe (12d)", time: "vence 2026-06-23" },
  { type: "info", text: "Sin alertas de documentos", time: "ahora" },
];

describe("AlertPanel (RF06)", () => {
  it("muestra el título Alertas activas", () => {
    render(<AlertPanel alerts={[]} />);
    expect(screen.getByText("Alertas activas")).toBeInTheDocument();
  });

  it("muestra el mensaje vacío cuando no hay alertas", () => {
    render(<AlertPanel alerts={[]} />);
    expect(screen.getByText("Sin alertas activas")).toBeInTheDocument();
  });

  it("renderiza el texto y la hora de cada alerta", () => {
    render(<AlertPanel alerts={ALERTAS} />);
    for (const a of ALERTAS) {
      expect(screen.getByText(a.text)).toBeInTheDocument();
      expect(screen.getByText(a.time)).toBeInTheDocument();
    }
  });

  it("no muestra el mensaje vacío cuando hay alertas", () => {
    render(<AlertPanel alerts={ALERTAS} />);
    expect(screen.queryByText("Sin alertas activas")).not.toBeInTheDocument();
  });

  it("colorea el punto según el tipo de alerta", () => {
    const { container } = render(<AlertPanel alerts={ALERTAS} />);
    // El dot es el primer div de cada item (width 7px, borderRadius 50%)
    const dots = [...container.querySelectorAll("div")].filter(
      d => d.style.borderRadius === "50%" && d.style.width === "7px",
    );
    expect(dots).toHaveLength(3);
    expect(dots[0].style.background).toBe("rgb(226, 75, 74)");  // danger #E24B4A
    expect(dots[1].style.background).toBe("rgb(239, 159, 39)"); // warn   #EF9F27
    expect(dots[2].style.background).toBe("rgb(55, 138, 221)"); // info   #378ADD
  });

  it("usa gris para un tipo desconocido", () => {
    const { container } = render(
      <AlertPanel alerts={[{ type: "otro", text: "Alerta rara", time: "ahora" }]} />,
    );
    const dot = [...container.querySelectorAll("div")].find(
      d => d.style.borderRadius === "50%" && d.style.width === "7px",
    );
    expect(dot.style.background).toBe("rgb(136, 136, 136)"); // fallback #888
  });
});
