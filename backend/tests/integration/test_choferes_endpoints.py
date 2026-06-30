"""Pruebas de integración de /api/choferes/* (RF04 — crítico RNF05).

Registro con acceso al portal, scope por área del supervisor, estado y portal del chofer.
"""
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


def _payload_chofer(area_id: int, **overrides):
    base = {
        "dni": "45892314",
        "nombres": "Roberto",
        "apellidos": "Castillo Vera",
        "fecha_nacimiento": "1988-03-12",
        "area_id": area_id,
        "numero_licencia": "LIC-45892314",
        "tipo_licencia": "A-IIIB",
        "fec_vence_licencia": "2027-01-01",
        "fec_vence_certif_prot": "2027-01-01",
    }
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_choferes_ok(client, auth_admin_headers, chofer_norte, chofer_sur):
    resp = client.get("/api/choferes/", headers=auth_admin_headers)
    assert resp.status_code == 200
    dnis = {c["dni"] for c in resp.json()}
    assert dnis == {"44156789", "43678912"}


def test_listar_choferes_filtro_area(client, auth_admin_headers, chofer_norte, chofer_sur, area_sur):
    resp = client.get(f"/api/choferes/?area_id={area_sur.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["dni"] == "43678912"


def test_listar_choferes_sin_token_401(client):
    assert client.get("/api/choferes/").status_code == 401


def test_obtener_chofer_ok(client, auth_admin_headers, chofer_norte):
    resp = client.get(f"/api/choferes/{chofer_norte.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["dni"] == "44156789"


def test_obtener_chofer_404(client, auth_admin_headers):
    resp = client.get("/api/choferes/999", headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Registro con acceso al portal ─────────────────────────
def test_registrar_chofer_admin_201_con_acceso(client, auth_admin_headers, area_norte):
    resp = client.post("/api/choferes/", json=_payload_chofer(area_norte.id),
                       headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["dni"] == "45892314"
    assert body["acceso_portal"]["email"] == "45892314@metrohub.gob.pe"
    assert body["acceso_portal"]["debe_cambiar_password"] is True


def test_registrar_chofer_supervisor_su_area_201(client, auth_supervisor_norte_headers, area_norte):
    resp = client.post("/api/choferes/", json=_payload_chofer(area_norte.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 201


def test_registrar_chofer_supervisor_otra_area_403(client, auth_supervisor_norte_headers, area_sur):
    resp = client.post("/api/choferes/", json=_payload_chofer(area_sur.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
    assert "área operativa" in resp.json()["detail"]


def test_registrar_chofer_chofer_403(client, auth_chofer_headers, area_norte):
    resp = client.post("/api/choferes/", json=_payload_chofer(area_norte.id),
                       headers=auth_chofer_headers)
    assert resp.status_code == 403


def test_registrar_chofer_dni_duplicado_400(client, auth_admin_headers, chofer_norte, area_norte):
    resp = client.post("/api/choferes/", json=_payload_chofer(area_norte.id, dni="44156789"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "DNI" in resp.json()["detail"]


# ── Cambio de estado ──────────────────────────────────────
def test_actualizar_estado_ok(client, auth_admin_headers, chofer_norte):
    resp = client.patch(f"/api/choferes/{chofer_norte.id}/estado",
                        json={"estado": "vacaciones"}, headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["chofer"]["estado"] == "vacaciones"


def test_actualizar_estado_invalido_400(client, auth_admin_headers, chofer_norte):
    resp = client.patch(f"/api/choferes/{chofer_norte.id}/estado",
                        json={"estado": "jubilado"}, headers=auth_admin_headers)
    assert resp.status_code == 400


def test_actualizar_estado_404(client, auth_admin_headers):
    resp = client.patch("/api/choferes/999/estado",
                        json={"estado": "activo"}, headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Alertas de documentos ─────────────────────────────────
def test_alertas_documentos_ok(client, auth_admin_headers, chofer_norte):
    resp = client.get("/api/choferes/alertas/documentos", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert "total_alertas" in resp.json()


# ── Portal del chofer (/me/asignaciones) ──────────────────
def test_mis_asignaciones_chofer_ok(client, auth_chofer_headers):
    resp = client.get("/api/choferes/me/asignaciones?fecha=2026-06-01",
                      headers=auth_chofer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["asignaciones"] == []


def test_mis_asignaciones_admin_403(client, auth_admin_headers):
    resp = client.get("/api/choferes/me/asignaciones", headers=auth_admin_headers)
    assert resp.status_code == 403
