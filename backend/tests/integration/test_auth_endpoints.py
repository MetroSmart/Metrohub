"""Integration tests para /api/auth/* (RF01)."""
import pytest


def test_login_admin_ok(client, usuario_admin):
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin.atu@metrohub.gob.pe", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["rol"] == "admin_atu"
    assert body["area_id"] is None
    assert body["access_token"]


def test_login_supervisor_incluye_area(client, usuario_supervisor_norte):
    resp = client.post(
        "/api/auth/login",
        data={"username": "sup.norte@metrohub.gob.pe", "password": "norte123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rol"] == "supervisor_area"
    assert body["area_id"] == 1


def test_login_chofer_ok(client, acceso_chofer_norte):
    resp = client.post(
        "/api/auth/login",
        data={"username": "jhuaman@metrohub.gob.pe", "password": "44156789"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rol"] == "chofer"
    assert body["chofer_id"] == acceso_chofer_norte.chofer_id


def test_login_credenciales_invalidas(client, usuario_admin):
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin.atu@metrohub.gob.pe", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_usuario_inexistente(client):
    resp = client.post(
        "/api/auth/login",
        data={"username": "nadie@nada.com", "password": "x"},
    )
    assert resp.status_code == 401


def test_me_admin(client, usuario_admin, auth_admin_headers):
    resp = client.get("/api/auth/me", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == usuario_admin.email
    assert body["rol"] == "admin_atu"


def test_me_supervisor(client, usuario_supervisor_norte, auth_supervisor_norte_headers):
    resp = client.get("/api/auth/me", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.json()["area_id"] == 1


def test_me_chofer(client, acceso_chofer_norte, auth_chofer_headers):
    resp = client.get("/api/auth/me", headers=auth_chofer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["rol"] == "chofer"
    assert body["chofer_id"] == acceso_chofer_norte.chofer_id


def test_me_sin_token_devuelve_401(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_token_invalido_devuelve_401(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer xxx"})
    assert resp.status_code == 401


def test_cambiar_password_solo_chofer(client, auth_admin_headers):
    resp = client.post(
        "/api/auth/cambiar-password-primer-ingreso",
        headers=auth_admin_headers,
        json={"password_actual": "x", "password_nueva": "nueva-clave"},
    )
    assert resp.status_code == 403
