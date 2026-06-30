"""Pruebas de integración de /api/disponibilidad/* (RF04)."""
from datetime import date

import pytest

from app.models.chofer import Chofer


@pytest.fixture
def chofer_sur(db_session, area_sur) -> Chofer:
    c = Chofer(
        dni="43678912", nombres="Miguel Ángel", apellidos="Torres Huanca",
        fecha_nacimiento=date(1986, 7, 10), area_id=area_sur.id,
        numero_licencia="LIC-43678912", tipo_licencia="A-IIIB",
        fec_vence_licencia=date(2027, 1, 1), fec_vence_certif_prot=date(2027, 1, 1),
        estado="activo")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def _payload(chofer_id, **overrides):
    base = {"chofer_id": chofer_id, "fecha": "2026-06-01", "hora_desde": "08:00",
            "hora_hasta": "14:00", "motivo": "descanso"}
    base.update(overrides)
    return base


# ── Listado ───────────────────────────────────────────────
def test_listar_disponibilidad_vacio(client, auth_admin_headers):
    resp = client.get("/api/disponibilidad/", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_listar_sin_token_401(client):
    assert client.get("/api/disponibilidad/").status_code == 401


# ── Registro ──────────────────────────────────────────────
def test_registrar_admin_201(client, auth_admin_headers, chofer_norte):
    resp = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id),
                       headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["motivo"] == "descanso"
    assert body["hora_desde"] == "08:00"


def test_registrar_supervisor_su_area_201(client, auth_supervisor_norte_headers, chofer_norte):
    resp = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 201


def test_registrar_supervisor_otra_area_403(client, auth_supervisor_norte_headers, chofer_sur):
    resp = client.post("/api/disponibilidad/", json=_payload(chofer_sur.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
    assert "su área" in resp.json()["detail"]


def test_registrar_chofer_403(client, auth_chofer_headers, chofer_norte):
    resp = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id),
                       headers=auth_chofer_headers)
    assert resp.status_code == 403


def test_registrar_motivo_invalido_400(client, auth_admin_headers, chofer_norte):
    resp = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id, motivo="feriado"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400


def test_registrar_hora_invalida_422(client, auth_admin_headers, chofer_norte):
    # hora_hasta <= hora_desde lo rechaza el schema (422)
    resp = client.post("/api/disponibilidad/",
                       json=_payload(chofer_norte.id, hora_desde="14:00", hora_hasta="08:00"),
                       headers=auth_admin_headers)
    assert resp.status_code == 422


# ── Eliminación ───────────────────────────────────────────
def test_eliminar_admin_204(client, auth_admin_headers, chofer_norte):
    creada = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id),
                         headers=auth_admin_headers).json()
    resp = client.delete(f"/api/disponibilidad/{creada['id']}", headers=auth_admin_headers)
    assert resp.status_code == 204


def test_eliminar_supervisor_403(client, auth_supervisor_norte_headers, auth_admin_headers,
                                 chofer_norte):
    creada = client.post("/api/disponibilidad/", json=_payload(chofer_norte.id),
                         headers=auth_admin_headers).json()
    resp = client.delete(f"/api/disponibilidad/{creada['id']}",
                         headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_eliminar_404(client, auth_admin_headers):
    assert client.delete("/api/disponibilidad/999", headers=auth_admin_headers).status_code == 404
