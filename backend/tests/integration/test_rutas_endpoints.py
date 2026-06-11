"""SCRUM-QA-18: pruebas de integración de /api/rutas/* (RF02).

CRUD completo por el admin y 403 para roles sin permiso de escritura.
"""
from datetime import time

import pytest

from app.models.ruta import Ruta
from app.models.estacion import Estacion


@pytest.fixture
def ruta_activa(db_session) -> Ruta:
    ruta = Ruta(
        codigo="SIT-1",
        nombre="Naranjal - Matellini",
        tipo="regular",
        hora_inicio=time(5, 0),
        hora_fin=time(23, 0),
        frecuencia_min=10,
        activa=True,
    )
    db_session.add(ruta)
    db_session.commit()
    db_session.refresh(ruta)
    return ruta


@pytest.fixture
def ruta_inactiva(db_session) -> Ruta:
    ruta = Ruta(
        codigo="N-205",
        nombre="Nocturna Centro",
        tipo="nocturna",
        hora_inicio=time(23, 0),
        hora_fin=time(4, 30),
        frecuencia_min=30,
        activa=False,
    )
    db_session.add(ruta)
    db_session.commit()
    db_session.refresh(ruta)
    return ruta


@pytest.fixture
def estacion_norte(db_session) -> Estacion:
    est = Estacion(
        codigo="EST-001",
        nombre="Estación Naranjal",
        tipo="terminal",
        tramo="norte",
        orden_troncal=1,
        activa=True,
    )
    db_session.add(est)
    db_session.commit()
    db_session.refresh(est)
    return est


def _payload_ruta(**overrides):
    base = {
        "codigo": "SIT-2",
        "nombre": "Ramal Centro Cívico",
        "tipo": "expreso",
        "hora_inicio": "06:00",
        "hora_fin": "22:00",
        "frecuencia_min": 8,
    }
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_rutas_ok(client, auth_admin_headers, ruta_activa, ruta_inactiva):
    resp = client.get("/api/rutas/", headers=auth_admin_headers)
    assert resp.status_code == 200
    codigos = {r["codigo"] for r in resp.json()}
    assert codigos == {"SIT-1", "N-205"}


def test_listar_rutas_solo_activas(client, auth_admin_headers, ruta_activa, ruta_inactiva):
    resp = client.get("/api/rutas/?solo_activas=true", headers=auth_admin_headers)
    assert resp.status_code == 200
    rutas = resp.json()
    assert len(rutas) == 1
    assert rutas[0]["codigo"] == "SIT-1"


def test_listar_rutas_sin_token_401(client, ruta_activa):
    resp = client.get("/api/rutas/")
    assert resp.status_code == 401


def test_obtener_ruta_ok(client, auth_admin_headers, ruta_activa):
    resp = client.get(f"/api/rutas/{ruta_activa.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["codigo"] == "SIT-1"
    assert body["frecuencia_min"] == 10


def test_obtener_ruta_404(client, auth_admin_headers):
    resp = client.get("/api/rutas/999", headers=auth_admin_headers)
    assert resp.status_code == 404
    assert "no encontrada" in resp.json()["detail"]


# ── Creación ──────────────────────────────────────────────
def test_crear_ruta_admin_201(client, auth_admin_headers):
    resp = client.post("/api/rutas/", json=_payload_ruta(), headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["codigo"] == "SIT-2"
    assert body["activa"] is True
    assert body["id"] is not None


def test_crear_ruta_supervisor_403(client, auth_supervisor_norte_headers):
    resp = client.post("/api/rutas/", json=_payload_ruta(), headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
    assert "Administrador ATU" in resp.json()["detail"]


def test_crear_ruta_chofer_403(client, auth_chofer_headers):
    resp = client.post("/api/rutas/", json=_payload_ruta(), headers=auth_chofer_headers)
    assert resp.status_code == 403


def test_crear_ruta_frecuencia_invalida_422(client, auth_admin_headers):
    resp = client.post("/api/rutas/", json=_payload_ruta(frecuencia_min=61),
                       headers=auth_admin_headers)
    assert resp.status_code == 422


# ── Actualización ─────────────────────────────────────────
def test_actualizar_ruta_admin_ok(client, auth_admin_headers, ruta_activa):
    resp = client.put(f"/api/rutas/{ruta_activa.id}",
                      json=_payload_ruta(codigo="SIT-1", nombre="Naranjal - Matellini (ext.)"),
                      headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Naranjal - Matellini (ext.)"


def test_actualizar_ruta_supervisor_403(client, auth_supervisor_norte_headers, ruta_activa):
    resp = client.put(f"/api/rutas/{ruta_activa.id}", json=_payload_ruta(),
                      headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_actualizar_ruta_404(client, auth_admin_headers):
    resp = client.put("/api/rutas/999", json=_payload_ruta(), headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Cambio de estado ──────────────────────────────────────
def test_cambiar_estado_admin_desactiva(client, auth_admin_headers, ruta_activa):
    resp = client.patch(f"/api/rutas/{ruta_activa.id}/estado?activa=false",
                        headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "desactivada" in body["mensaje"]
    assert body["ruta"]["activa"] is False


def test_cambiar_estado_supervisor_403(client, auth_supervisor_norte_headers, ruta_activa):
    resp = client.patch(f"/api/rutas/{ruta_activa.id}/estado?activa=false",
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_cambiar_estado_404(client, auth_admin_headers):
    resp = client.patch("/api/rutas/999/estado?activa=true", headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Estaciones de la ruta ─────────────────────────────────
def test_listar_estaciones_de_ruta_ok(client, auth_admin_headers, ruta_activa, estacion_norte):
    asig = client.post(f"/api/rutas/{ruta_activa.id}/estaciones",
                       json={"estacion_id": estacion_norte.id, "orden": 1, "tiempo_est_min": 5},
                       headers=auth_admin_headers)
    assert asig.status_code == 201

    resp = client.get(f"/api/rutas/{ruta_activa.id}/estaciones", headers=auth_admin_headers)
    assert resp.status_code == 200
    recorrido = resp.json()
    assert len(recorrido) == 1
    assert recorrido[0]["codigo"] == "EST-001"
    assert recorrido[0]["orden"] == 1
    assert recorrido[0]["tiempo_est_min"] == 5


def test_listar_estaciones_ruta_404(client, auth_admin_headers):
    resp = client.get("/api/rutas/999/estaciones", headers=auth_admin_headers)
    assert resp.status_code == 404


def test_asignar_estacion_supervisor_403(client, auth_supervisor_norte_headers,
                                         ruta_activa, estacion_norte):
    resp = client.post(f"/api/rutas/{ruta_activa.id}/estaciones",
                       json={"estacion_id": estacion_norte.id, "orden": 1},
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_asignar_estacion_ruta_404(client, auth_admin_headers, estacion_norte):
    resp = client.post("/api/rutas/999/estaciones",
                       json={"estacion_id": estacion_norte.id, "orden": 1},
                       headers=auth_admin_headers)
    assert resp.status_code == 404


def test_asignar_estacion_inexistente_404(client, auth_admin_headers, ruta_activa):
    resp = client.post(f"/api/rutas/{ruta_activa.id}/estaciones",
                       json={"estacion_id": 999, "orden": 1},
                       headers=auth_admin_headers)
    assert resp.status_code == 404
    assert "Estación" in resp.json()["detail"]


def test_desasignar_estacion_admin_204(client, auth_admin_headers, ruta_activa, estacion_norte):
    client.post(f"/api/rutas/{ruta_activa.id}/estaciones",
                json={"estacion_id": estacion_norte.id, "orden": 1},
                headers=auth_admin_headers)

    resp = client.delete(f"/api/rutas/{ruta_activa.id}/estaciones/{estacion_norte.id}",
                         headers=auth_admin_headers)
    assert resp.status_code == 204

    recorrido = client.get(f"/api/rutas/{ruta_activa.id}/estaciones",
                           headers=auth_admin_headers).json()
    assert recorrido == []


def test_desasignar_estacion_supervisor_403(client, auth_supervisor_norte_headers,
                                            ruta_activa, estacion_norte):
    resp = client.delete(f"/api/rutas/{ruta_activa.id}/estaciones/{estacion_norte.id}",
                         headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_desasignar_estacion_no_asignada_404(client, auth_admin_headers,
                                             ruta_activa, estacion_norte):
    resp = client.delete(f"/api/rutas/{ruta_activa.id}/estaciones/{estacion_norte.id}",
                         headers=auth_admin_headers)
    assert resp.status_code == 404
