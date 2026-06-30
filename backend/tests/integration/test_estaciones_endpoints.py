"""Pruebas de integración de /api/estaciones/* (RF02)."""
import pytest

from app.models.estacion import Estacion


@pytest.fixture
def estacion_norte(db_session) -> Estacion:
    e = Estacion(codigo="EST-001", nombre="Estación Naranjal", tipo="terminal",
                 tramo="norte", orden_troncal=1, activa=True)
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


def _payload(**overrides):
    base = {"codigo": "EST-002", "nombre": "Estación Central", "tipo": "intermedia",
            "tramo": "centro", "orden_troncal": 2, "activa": True}
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_estaciones_ok(client, auth_admin_headers, estacion_norte):
    resp = client.get("/api/estaciones/", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_listar_estaciones_filtro_tramo(client, auth_admin_headers, estacion_norte):
    assert client.get("/api/estaciones/?tramo=norte", headers=auth_admin_headers).json()["total"] == 1
    assert client.get("/api/estaciones/?tramo=sur", headers=auth_admin_headers).json()["total"] == 0


def test_listar_estaciones_sin_token_401(client):
    assert client.get("/api/estaciones/").status_code == 401


def test_obtener_estacion_ok(client, auth_admin_headers, estacion_norte):
    resp = client.get(f"/api/estaciones/{estacion_norte.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["codigo"] == "EST-001"


def test_obtener_estacion_404(client, auth_admin_headers):
    assert client.get("/api/estaciones/999", headers=auth_admin_headers).status_code == 404


# ── Creación ──────────────────────────────────────────────
def test_crear_estacion_admin_201(client, auth_admin_headers):
    resp = client.post("/api/estaciones/", json=_payload(), headers=auth_admin_headers)
    assert resp.status_code == 201
    assert resp.json()["codigo"] == "EST-002"


def test_crear_estacion_supervisor_403(client, auth_supervisor_norte_headers):
    resp = client.post("/api/estaciones/", json=_payload(), headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_crear_estacion_tipo_invalido_400(client, auth_admin_headers):
    resp = client.post("/api/estaciones/", json=_payload(tipo="expresa"), headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Tipo inválido" in resp.json()["detail"]


def test_crear_estacion_tramo_invalido_400(client, auth_admin_headers):
    resp = client.post("/api/estaciones/", json=_payload(tramo="este"), headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Tramo inválido" in resp.json()["detail"]


def test_crear_estacion_codigo_duplicado_400(client, auth_admin_headers, estacion_norte):
    resp = client.post("/api/estaciones/", json=_payload(codigo="EST-001"), headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Ya existe" in resp.json()["detail"]
