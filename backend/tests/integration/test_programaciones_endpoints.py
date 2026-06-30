"""Pruebas de integración de /api/programaciones/* (RF03)."""
from datetime import date

import pytest

from app.models.programacion import Programacion


@pytest.fixture
def programacion(db_session, usuario_admin) -> Programacion:
    p = Programacion(nombre="Semana piloto", fecha_inicio=date(2026, 6, 1),
                     fecha_fin=date(2026, 6, 7), estado="borrador", creado_por=usuario_admin.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def programacion_aprobada(db_session, usuario_admin) -> Programacion:
    p = Programacion(nombre="Semana aprobada", fecha_inicio=date(2026, 6, 8),
                     fecha_fin=date(2026, 6, 14), estado="aprobada", creado_por=usuario_admin.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _payload(**overrides):
    base = {"nombre": "Nueva semana", "fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-07"}
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_programaciones_ok(client, auth_admin_headers, programacion):
    resp = client.get("/api/programaciones/", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_listar_filtro_estado(client, auth_admin_headers, programacion, programacion_aprobada):
    resp = client.get("/api/programaciones/?estado=aprobada", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_listar_sin_token_401(client):
    assert client.get("/api/programaciones/").status_code == 401


def test_obtener_programacion_ok(client, auth_admin_headers, programacion):
    resp = client.get(f"/api/programaciones/{programacion.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Semana piloto"


def test_obtener_programacion_404(client, auth_admin_headers):
    assert client.get("/api/programaciones/999", headers=auth_admin_headers).status_code == 404


# ── Creación ──────────────────────────────────────────────
def test_crear_programacion_admin_201(client, auth_admin_headers):
    resp = client.post("/api/programaciones/", json=_payload(), headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["nombre"] == "Nueva semana"
    assert body["estado"] == "borrador"


def test_crear_programacion_supervisor_403(client, auth_supervisor_norte_headers):
    resp = client.post("/api/programaciones/", json=_payload(), headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_crear_programacion_fechas_invalidas_422(client, auth_admin_headers):
    resp = client.post("/api/programaciones/",
                       json=_payload(fecha_inicio="2026-07-07", fecha_fin="2026-07-01"),
                       headers=auth_admin_headers)
    assert resp.status_code == 422


# ── Eliminación ───────────────────────────────────────────
def test_eliminar_borrador_admin_204(client, auth_admin_headers, programacion):
    resp = client.delete(f"/api/programaciones/{programacion.id}", headers=auth_admin_headers)
    assert resp.status_code == 204


def test_eliminar_supervisor_403(client, auth_supervisor_norte_headers, programacion):
    resp = client.delete(f"/api/programaciones/{programacion.id}",
                         headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_eliminar_aprobada_409(client, auth_admin_headers, programacion_aprobada):
    resp = client.delete(f"/api/programaciones/{programacion_aprobada.id}",
                         headers=auth_admin_headers)
    assert resp.status_code == 409


def test_eliminar_404(client, auth_admin_headers):
    assert client.delete("/api/programaciones/999", headers=auth_admin_headers).status_code == 404
