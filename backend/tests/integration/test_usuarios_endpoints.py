"""SCRUM-QA-30: pruebas de integración de /api/usuarios/* (catálogos internos).

Todo el CRUD es exclusivo del admin_atu; el supervisor recibe 403.
"""
import pytest


def _payload_supervisor(area_id: int, **overrides):
    base = {
        "email": "sup.nuevo@metrohub.gob.pe",
        "password": "temporal123",
        "nombre": "Carla",
        "apellidos": "Reyes Soto",
        "dni": "20000001",
        "rol": "supervisor_area",
        "area_id": area_id,
    }
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_usuarios_admin_ok(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.get("/api/usuarios/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2  # admin + supervisor
    emails = {u["email"] for u in body["usuarios"]}
    assert "sup.norte@metrohub.gob.pe" in emails


def test_listar_usuarios_filtro_rol(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.get("/api/usuarios/?rol=supervisor_area", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["usuarios"][0]["rol"] == "supervisor_area"


def test_listar_usuarios_supervisor_403(client, auth_supervisor_norte_headers):
    resp = client.get("/api/usuarios/", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_obtener_usuario_ok(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.get(f"/api/usuarios/{usuario_supervisor_norte.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "sup.norte@metrohub.gob.pe"
    assert body["area_id"] == usuario_supervisor_norte.area_id


def test_obtener_usuario_404(client, auth_admin_headers):
    resp = client.get("/api/usuarios/999", headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Creación ──────────────────────────────────────────────
def test_crear_supervisor_admin_201(client, auth_admin_headers, area_norte):
    resp = client.post("/api/usuarios/", json=_payload_supervisor(area_norte.id),
                       headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["rol"] == "supervisor_area"
    assert body["area_id"] == area_norte.id
    assert body["activo"] is True


def test_crear_admin_sin_area_201(client, auth_admin_headers):
    payload = _payload_supervisor(0, rol="admin_atu",
                                  email="admin2@metrohub.gob.pe", dni="20000002")
    payload["area_id"] = None
    resp = client.post("/api/usuarios/", json=payload, headers=auth_admin_headers)
    assert resp.status_code == 201
    assert resp.json()["area_id"] is None


def test_crear_usuario_supervisor_403(client, auth_supervisor_norte_headers, area_norte):
    resp = client.post("/api/usuarios/", json=_payload_supervisor(area_norte.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_crear_usuario_rol_invalido_400(client, auth_admin_headers, area_norte):
    resp = client.post("/api/usuarios/", json=_payload_supervisor(area_norte.id, rol="chofer"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Rol inválido" in resp.json()["detail"]


def test_crear_supervisor_sin_area_400(client, auth_admin_headers):
    payload = _payload_supervisor(0)
    payload["area_id"] = None
    resp = client.post("/api/usuarios/", json=payload, headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "area_id" in resp.json()["detail"]


def test_crear_admin_con_area_400(client, auth_admin_headers, area_norte):
    resp = client.post("/api/usuarios/",
                       json=_payload_supervisor(area_norte.id, rol="admin_atu"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "no puede tener area_id" in resp.json()["detail"]


@pytest.mark.parametrize("dni", ["1234567", "123456789", "1234567a", "abcdefgh"])
def test_crear_usuario_dni_invalido_400(client, auth_admin_headers, area_norte, dni):
    resp = client.post("/api/usuarios/", json=_payload_supervisor(area_norte.id, dni=dni),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "DNI" in resp.json()["detail"]


def test_crear_usuario_email_duplicado_400(client, auth_admin_headers,
                                           usuario_supervisor_norte, area_norte):
    resp = client.post("/api/usuarios/",
                       json=_payload_supervisor(area_norte.id,
                                                email="sup.norte@metrohub.gob.pe"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "email" in resp.json()["detail"]


def test_crear_usuario_dni_duplicado_400(client, auth_admin_headers,
                                         usuario_supervisor_norte, area_norte):
    resp = client.post("/api/usuarios/",
                       json=_payload_supervisor(area_norte.id, dni="10000002"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "DNI" in resp.json()["detail"]


# ── Actualización ─────────────────────────────────────────
def test_actualizar_usuario_ok(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}",
                        json={"nombre": "Supervisora", "activo": False},
                        headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["nombre"] == "Supervisora"
    assert body["activo"] is False


def test_actualizar_usuario_sin_campos_400(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}", json={},
                        headers=auth_admin_headers)
    assert resp.status_code == 400


def test_actualizar_usuario_404(client, auth_admin_headers):
    resp = client.patch("/api/usuarios/999", json={"nombre": "X"}, headers=auth_admin_headers)
    assert resp.status_code == 404


def test_actualizar_usuario_supervisor_403(client, auth_supervisor_norte_headers,
                                           usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}",
                        json={"activo": False}, headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


# ── Cambio de contraseña ──────────────────────────────────
def test_cambiar_password_ok(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}/password",
                        json={"nueva_password": "nueva-clave-9"},
                        headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["mensaje"] == "Contraseña actualizada"

    # El supervisor puede loguearse con la nueva contraseña
    login = client.post("/api/auth/login",
                        data={"username": "sup.norte@metrohub.gob.pe",
                              "password": "nueva-clave-9"})
    assert login.status_code == 200


def test_cambiar_password_corta_400(client, auth_admin_headers, usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}/password",
                        json={"nueva_password": "abc12"},
                        headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "6 caracteres" in resp.json()["detail"]


def test_cambiar_password_404(client, auth_admin_headers):
    resp = client.patch("/api/usuarios/999/password",
                        json={"nueva_password": "nueva-clave-9"},
                        headers=auth_admin_headers)
    assert resp.status_code == 404


def test_cambiar_password_supervisor_403(client, auth_supervisor_norte_headers,
                                         usuario_supervisor_norte):
    resp = client.patch(f"/api/usuarios/{usuario_supervisor_norte.id}/password",
                        json={"nueva_password": "intrusa-123"},
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
