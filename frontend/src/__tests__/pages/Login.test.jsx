import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";
import Login from "../../pages/Login.jsx";

describe("Login (RF01)", () => {
  it("muestra el formulario con campos requeridos", () => {
    render(<Login onLogin={() => {}} />);
    expect(screen.getByPlaceholderText(/usuario@atu/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("••••••••")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ingresar/i })).toBeInTheDocument();
  });

  it("muestra error si faltan campos", async () => {
    const user = userEvent.setup();
    render(<Login onLogin={() => {}} />);
    await user.click(screen.getByRole("button", { name: /ingresar/i }));
    expect(await screen.findByText(/completa todos los campos/i)).toBeInTheDocument();
  });

  it("login exitoso llama onLogin con los datos del usuario y guarda token", async () => {
    const user = userEvent.setup();
    const onLogin = vi.fn();
    render(<Login onLogin={onLogin} />);

    await user.type(screen.getByPlaceholderText(/usuario@atu/i), "admin.atu@metrohub.gob.pe");
    await user.type(screen.getByPlaceholderText("••••••••"), "admin123");
    await user.click(screen.getByRole("button", { name: /ingresar/i }));

    await vi.waitFor(() => expect(onLogin).toHaveBeenCalledTimes(1));
    expect(onLogin.mock.calls[0][0]).toMatchObject({
      email: "admin.atu@metrohub.gob.pe",
      role: "admin_atu",
    });
    expect(localStorage.getItem("metrohub_access_token")).toBe("fake-jwt-admin");
  });

  it("credenciales inválidas incrementan el contador de intentos", async () => {
    const user = userEvent.setup();
    render(<Login onLogin={() => {}} />);

    await user.type(screen.getByPlaceholderText(/usuario@atu/i), "x@y.com");
    await user.type(screen.getByPlaceholderText("••••••••"), "bad");
    await user.click(screen.getByRole("button", { name: /ingresar/i }));

    expect(await screen.findByText(/intento 1\/5/i)).toBeInTheDocument();
  });

  it("bloquea el formulario tras 5 intentos fallidos", async () => {
    const user = userEvent.setup();
    render(<Login onLogin={() => {}} />);

    await user.type(screen.getByPlaceholderText(/usuario@atu/i), "x@y.com");
    await user.type(screen.getByPlaceholderText("••••••••"), "bad");

    const submit = screen.getByRole("button", { name: /ingresar/i });
    for (let i = 0; i < 5; i++) {
      await user.click(submit);
      await screen.findByText(/intento|bloqueada/i);
    }
    expect(await screen.findByText(/cuenta bloqueada/i)).toBeInTheDocument();
  });

  it("muestra error de conexión si la red falla", async () => {
    server.use(
      http.post("http://localhost:8000/api/auth/login", () => HttpResponse.error())
    );
    const user = userEvent.setup();
    render(<Login onLogin={() => {}} />);

    await user.type(screen.getByPlaceholderText(/usuario@atu/i), "a@b.com");
    await user.type(screen.getByPlaceholderText("••••••••"), "x");
    await user.click(screen.getByRole("button", { name: /ingresar/i }));

    expect(await screen.findByText(/no se pudo conectar/i)).toBeInTheDocument();
  });
});
