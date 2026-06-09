import { http, HttpResponse } from "msw";

const API = "http://localhost:8000";

export const handlers = [
  // Login OK por defecto. Tests pueden sobreescribir con server.use(...)
  http.post(`${API}/api/auth/login`, async ({ request }) => {
    const form = await request.formData();
    const username = form.get("username");
    const password = form.get("password");

    if (username === "admin.atu@metrohub.gob.pe" && password === "admin123") {
      return HttpResponse.json({
        access_token: "fake-jwt-admin",
        token_type: "bearer",
        rol: "admin_atu",
        nombre: "Admin ATU",
        chofer_id: null,
        area_id: null,
        debe_cambiar_password: false,
      });
    }
    return new HttpResponse(JSON.stringify({ detail: "Credenciales incorrectas" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }),
];
