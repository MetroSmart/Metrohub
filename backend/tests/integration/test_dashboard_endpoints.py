"""SCRUM-QA-22: pruebas de integración de /api/dashboard (KPIs, RF06).

Redis se neutraliza con monkeypatch para que los KPIs salgan siempre de la BD
(SQLite en memoria) salvo en los tests de cache, que usan un FakeRedis.
"""
import json
from datetime import date, timedelta

import pytest

from app.models.ruta import Ruta
from app.models.bus import Bus
from app.models.chofer import Chofer
from app.models.conflicto import Conflicto


@pytest.fixture(autouse=True)
def sin_redis(monkeypatch):
    """Evita la conexión real (timeout de 2 s por request) y hace los tests deterministas."""
    monkeypatch.setattr("app.services.dashboard_service.get_redis", lambda: None)


class FakeRedis:
    def __init__(self, cached=None):
        self.cached = cached
        self.set_calls = []

    def get(self, key):
        return self.cached

    def set(self, key, value, ex=None):
        self.set_calls.append((key, value, ex))


@pytest.fixture
def datos_operativos(db_session, area_norte, chofer_norte):
    """Seed: 1 ruta activa + 1 inactiva, 1 bus operativo + 1 en taller,
    1 chofer con certificado por vencer y 1 conflicto abierto."""
    from datetime import time

    db_session.add_all([
        Ruta(codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
             hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True),
        Ruta(codigo="N-205", nombre="Nocturna", tipo="nocturna",
             hora_inicio=time(23, 0), hora_fin=time(4, 0), frecuencia_min=30, activa=False),
        Bus(placa="ABC-123", area_id=area_norte.id, tipo="articulado", estado="operativo"),
        Bus(placa="DEF-456", area_id=area_norte.id, tipo="convencional", estado="mantenimiento"),
        Chofer(
            dni="45678901", nombres="Rosa", apellidos="Quispe Mamani",
            fecha_nacimiento=date(1990, 3, 15), area_id=area_norte.id,
            numero_licencia="LIC-45678901", tipo_licencia="A-IIIB",
            fec_vence_licencia=date(2027, 1, 1),
            fec_vence_certif_prot=date.today() + timedelta(days=10),
            estado="activo",
        ),
        # FK de asignacion no se valida en SQLite; basta para el contador
        Conflicto(asignacion_id=1, tipo="solapamiento_turno", severidad="alta",
                  descripcion="Chofer con turnos solapados", resuelto=False),
    ])
    db_session.commit()


def test_dashboard_sin_token_401(client):
    resp = client.get("/api/dashboard/")
    assert resp.status_code == 401


def test_dashboard_kpis_en_cero(client, auth_admin_headers):
    resp = client.get("/api/dashboard/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["fecha"] == str(date.today())
    for kpi in ("rutas_activas", "choferes_activos", "buses_operativos",
                "asignaciones_hoy", "conflictos_abiertos", "certif_por_vencer_30d"):
        assert body[kpi] == 0


def test_dashboard_kpis_con_datos(client, auth_admin_headers, datos_operativos):
    resp = client.get("/api/dashboard/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["rutas_activas"] == 1          # solo SIT-1
    assert body["choferes_activos"] == 2       # chofer_norte + Rosa
    assert body["buses_operativos"] == 1       # solo ABC-123
    assert body["conflictos_abiertos"] == 1
    assert body["certif_por_vencer_30d"] == 1  # solo Rosa (chofer_norte vence 2027)
    assert body["asignaciones_hoy"] == 0


def test_dashboard_accesible_supervisor(client, auth_supervisor_norte_headers):
    resp = client.get("/api/dashboard/", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200


def test_dashboard_lee_cache_redis(client, auth_admin_headers, datos_operativos, monkeypatch):
    cacheado = {"fecha": "2026-06-10", "rutas_activas": 99}
    fake = FakeRedis(cached=json.dumps(cacheado))
    monkeypatch.setattr("app.services.dashboard_service.get_redis", lambda: fake)

    resp = client.get("/api/dashboard/", headers=auth_admin_headers)
    assert resp.status_code == 200
    # Devuelve el cache tal cual, ignorando los datos reales de la BD
    assert resp.json() == cacheado


def test_dashboard_escribe_cache_redis(client, auth_admin_headers, monkeypatch):
    fake = FakeRedis(cached=None)
    monkeypatch.setattr("app.services.dashboard_service.get_redis", lambda: fake)

    resp = client.get("/api/dashboard/", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert len(fake.set_calls) == 1
    key, value, ex = fake.set_calls[0]
    assert key == "dashboard:kpis"
    assert json.loads(value)["fecha"] == str(date.today())
    assert ex == 300
