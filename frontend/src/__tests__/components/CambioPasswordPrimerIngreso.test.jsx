import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CambioPasswordPrimerIngreso from "../../components/CambioPasswordPrimerIngreso.jsx";
import { api } from "../../api";

vi.mock("../../api", () => ({
  api: { post: vi.fn() },
}));

const USER = { name: "Rosa Quispe" };

function setup(props = {}) {
  const onComplete = vi.fn();
  const onLogout = vi.fn();
  const utils = render(
    <CambioPasswordPrimerIngreso
      user={USER}
      onComplete={onComplete}
      onLogout={onLogout}
      {...props}
    />,
  );
  // Inputs en orden: actual, nueva, confirmar
  const [actual, nueva, confirmar] = utils.container.querySelectorAll('input[type="password"]');
  return { onComplete, onLogout, actual, nueva, confirmar, ...utils };
}

describe("CambioPasswordPrimerIngreso (RF01)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("muestra el título, el saludo y la pista del DNI", () => {
    setup();
    expect(screen.getByText("Cambio de contraseña obligatorio")).toBeInTheDocument();
    expect(screen.getByText(/Hola, Rosa Quispe/)).toBeInTheDocument();
    expect(screen.getByText(/contraseña temporal es tu número de DNI/)).toBeInTheDocument();
  });

  it("exige completar todos los campos", async () => {
    const user = userEvent.setup();
    setup();
    await user.click(screen.getByRole("button", { name: "Actualizar contraseña" }));
    expect(screen.getByText("Completa todos los campos.")).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it("rechaza una nueva contraseña de menos de 8 caracteres", async () => {
    const user = userEvent.setup();
    const { actual, nueva, confirmar } = setup();
    await user.type(actual, "12345678");
    await user.type(nueva, "corta");
    await user.type(confirmar, "corta");
    await user.click(screen.getByRole("button", { name: "Actualizar contraseña" }));
    expect(
      screen.getByText("La nueva contraseña debe tener al menos 8 caracteres."),
    ).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it("rechaza cuando la confirmación no coincide", async () => {
    const user = userEvent.setup();
    const { actual, nueva, confirmar } = setup();
    await user.type(actual, "12345678");
    await user.type(nueva, "NuevaClave9");
    await user.type(confirmar, "OtraClave9");
    await user.click(screen.getByRole("button", { name: "Actualizar contraseña" }));
    expect(
      screen.getByText("La confirmación no coincide con la nueva contraseña."),
    ).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it("envía el cambio y llama onComplete cuando el API responde bien", async () => {
    const user = userEvent.setup();
    api.post.mockResolvedValueOnce({ ok: true });
    const { onComplete, actual, nueva, confirmar } = setup();
    await user.type(actual, "12345678");
    await user.type(nueva, "NuevaClave9");
    await user.type(confirmar, "NuevaClave9");
    await user.click(screen.getByRole("button", { name: "Actualizar contraseña" }));

    expect(api.post).toHaveBeenCalledWith("/api/auth/cambiar-password-primer-ingreso", {
      password_actual: "12345678",
      password_nueva: "NuevaClave9",
    });
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it("muestra el error del API y no llama onComplete cuando falla", async () => {
    const user = userEvent.setup();
    api.post.mockRejectedValueOnce(new Error("Contraseña actual incorrecta"));
    const { onComplete, actual, nueva, confirmar } = setup();
    await user.type(actual, "00000000");
    await user.type(nueva, "NuevaClave9");
    await user.type(confirmar, "NuevaClave9");
    await user.click(screen.getByRole("button", { name: "Actualizar contraseña" }));

    expect(screen.getByText("Contraseña actual incorrecta")).toBeInTheDocument();
    expect(onComplete).not.toHaveBeenCalled();
  });

  it("Cerrar sesión llama onLogout sin tocar el API", async () => {
    const user = userEvent.setup();
    const { onLogout } = setup();
    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));
    expect(onLogout).toHaveBeenCalledTimes(1);
    expect(api.post).not.toHaveBeenCalled();
  });
});
