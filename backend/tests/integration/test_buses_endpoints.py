"""SCRUM-QA-29: pruebas de integración de /api/buses/* con scope por area_id.

El admin gestiona toda la flota; el supervisor solo buses de su área.
"""
import pytest

from app.models.bus import Bus


@pytest.fixture
def bus_norte(db_session, area_norte) -> Bus:
    bus = Bus(placa="ABC-123", area_id=area_norte.id, tipo="articulado",
              anio=2020, capacidad_pasajeros=160, estado="operativo")
    db_session.add(bus)
    db_session.commit()
    db_session.refresh(bus)
    return bus


@pytest.fixture
def bus_sur(db_session, area_sur) -> Bus:
    bus = Bus(placa="DEF-456", area_id=area_sur.id, tipo="convencional",
              anio=2018, capacidad_pasajeros=80, estado="mantenimiento")
    db_session.add(bus)
    db_session.commit()
    db_session.refresh(bus)
    return bus


def _payload_bus(area_id: int, **overrides):
    base = {
        "placa": "GHI-789",
        "area_id": area_id,
        "tipo": "articulado",
        "anio": 2022,
        "capacidad_pasajeros": 160,
        "estado": "operativo",
    }
    base.update(overrides)
    return base


# ── Lectura ───────────────────────────────────────────────
def test_listar_buses_ok(client, auth_admin_headers, bus_norte, bus_sur):
    resp = client.get("/api/buses/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    placas = {b["placa"] for b in body["buses"]}
    assert placas == {"ABC-123", "DEF-456"}


def test_listar_buses_filtro_area(client, auth_admin_headers, bus_norte, bus_sur, area_norte):
    resp = client.get(f"/api/buses/?area_id={area_norte.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["buses"][0]["placa"] == "ABC-123"


def test_listar_buses_filtro_estado(client, auth_admin_headers, bus_norte, bus_sur):
    resp = client.get("/api/buses/?estado=mantenimiento", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["buses"][0]["placa"] == "DEF-456"


def test_obtener_bus_ok(client, auth_admin_headers, bus_norte):
    resp = client.get("/api/buses/ABC-123", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["tipo"] == "articulado"


def test_obtener_bus_404(client, auth_admin_headers):
    resp = client.get("/api/buses/ZZZ-999", headers=auth_admin_headers)
    assert resp.status_code == 404


def test_listar_buses_sin_token_401(client):
    resp = client.get("/api/buses/")
    assert resp.status_code == 401


# ── Creación con scope de área ────────────────────────────
def test_crear_bus_admin_201(client, auth_admin_headers, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id),
                       headers=auth_admin_headers)
    assert resp.status_code == 201
    assert resp.json()["placa"] == "GHI-789"


def test_crear_bus_supervisor_su_area_201(client, auth_supervisor_norte_headers, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 201


def test_crear_bus_supervisor_otra_area_403(client, auth_supervisor_norte_headers, area_sur):
    resp = client.post("/api/buses/", json=_payload_bus(area_sur.id),
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
    assert "su área operativa" in resp.json()["detail"]


def test_crear_bus_chofer_403(client, auth_chofer_headers, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id),
                       headers=auth_chofer_headers)
    assert resp.status_code == 403


def test_crear_bus_tipo_invalido_400(client, auth_admin_headers, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id, tipo="biarticulado"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Tipo inválido" in resp.json()["detail"]


def test_crear_bus_estado_invalido_400(client, auth_admin_headers, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id, estado="averiado"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Estado inválido" in resp.json()["detail"]


def test_crear_bus_placa_duplicada_400(client, auth_admin_headers, bus_norte, area_norte):
    resp = client.post("/api/buses/", json=_payload_bus(area_norte.id, placa="ABC-123"),
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "Ya existe" in resp.json()["detail"]


# ── Actualización con scope de área ───────────────────────
def test_actualizar_bus_supervisor_su_area_ok(client, auth_supervisor_norte_headers, bus_norte):
    resp = client.patch("/api/buses/ABC-123", json={"estado": "reparacion"},
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.json()["estado"] == "reparacion"


def test_actualizar_bus_supervisor_otra_area_403(client, auth_supervisor_norte_headers, bus_sur):
    resp = client.patch("/api/buses/DEF-456", json={"estado": "operativo"},
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_actualizar_bus_estado_invalido_400(client, auth_admin_headers, bus_norte):
    resp = client.patch("/api/buses/ABC-123", json={"estado": "averiado"},
                        headers=auth_admin_headers)
    assert resp.status_code == 400


def test_actualizar_bus_404(client, auth_admin_headers):
    resp = client.patch("/api/buses/ZZZ-999", json={"estado": "baja"},
                        headers=auth_admin_headers)
    assert resp.status_code == 404


# ── Eliminación con scope de área ─────────────────────────
def test_eliminar_bus_admin_204(client, auth_admin_headers, bus_norte):
    resp = client.delete("/api/buses/ABC-123", headers=auth_admin_headers)
    assert resp.status_code == 204
    assert client.get("/api/buses/ABC-123", headers=auth_admin_headers).status_code == 404


def test_eliminar_bus_supervisor_otra_area_403(client, auth_supervisor_norte_headers, bus_sur):
    resp = client.delete("/api/buses/DEF-456", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_eliminar_bus_404(client, auth_admin_headers):
    resp = client.delete("/api/buses/ZZZ-999", headers=auth_admin_headers)
    assert resp.status_code == 404
