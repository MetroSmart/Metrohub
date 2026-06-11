import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../test/server.js";
import { api, apiFetch } from "../api.js";

const API = "http://localhost:8000";

describe("api.js (cliente HTTP)", () => {
  beforeEach(() => {
    localStorage.setItem("metrohub_access_token", "tok-123");
  });

  it("envía el token Bearer y Content-Type JSON", async () => {
    let capturada;
    server.use(
      http.get(`${API}/api/ping`, ({ request }) => {
        capturada = request;
        return HttpResponse.json({ ok: true });
      }),
    );
    await apiFetch("/api/ping");
    expect(capturada.headers.get("Authorization")).toBe("Bearer tok-123");
    expect(capturada.headers.get("Content-Type")).toBe("application/json");
  });

  it("devuelve el JSON del body en una respuesta OK", async () => {
    server.use(
      http.get(`${API}/api/ping`, () => HttpResponse.json({ valor: 42 })),
    );
    await expect(apiFetch("/api/ping")).resolves.toEqual({ valor: 42 });
  });

  it("devuelve null en una respuesta 204", async () => {
    server.use(
      http.delete(`${API}/api/cosa/1`, () => new HttpResponse(null, { status: 204 })),
    );
    await expect(api.delete("/api/cosa/1")).resolves.toBeNull();
  });

  it("lanza el detail del backend cuando la respuesta es error", async () => {
    server.use(
      http.get(`${API}/api/ping`, () =>
        HttpResponse.json({ detail: "No autorizado" }, { status: 403 }),
      ),
    );
    await expect(apiFetch("/api/ping")).rejects.toThrow("No autorizado");
  });

  it("serializa un detail no-string del backend", async () => {
    server.use(
      http.get(`${API}/api/ping`, () =>
        HttpResponse.json({ detail: [{ msg: "campo requerido" }] }, { status: 422 }),
      ),
    );
    await expect(apiFetch("/api/ping")).rejects.toThrow("campo requerido");
  });

  it("usa status y statusText cuando el error no trae JSON", async () => {
    server.use(
      http.get(`${API}/api/ping`, () =>
        new HttpResponse("boom", { status: 500, statusText: "Internal Server Error" }),
      ),
    );
    await expect(apiFetch("/api/ping")).rejects.toThrow("500 Internal Server Error");
  });

  it("post/put/patch envían el body como JSON con su método", async () => {
    const llamadas = [];
    const captor = (metodo) =>
      http[metodo](`${API}/api/cosa`, async ({ request }) => {
        llamadas.push({ metodo, body: await request.json() });
        return HttpResponse.json({ ok: true });
      });
    server.use(captor("post"), captor("put"), captor("patch"));

    await api.post("/api/cosa", { a: 1 });
    await api.put("/api/cosa", { b: 2 });
    await api.patch("/api/cosa", { c: 3 });

    expect(llamadas).toEqual([
      { metodo: "post",  body: { a: 1 } },
      { metodo: "put",   body: { b: 2 } },
      { metodo: "patch", body: { c: 3 } },
    ]);
  });
});
