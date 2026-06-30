"""Unit tests para app.services.estacion_service (RF02)."""
from datetime import time

import pytest

from app.models.ruta import Ruta
from app.schemas.estacion import EstacionCrear, RutaEstacionAsignar
from app.services import estacion_service


def _datos(**overrides) -> EstacionCrear:
    base = dict(codigo="EST-001", nombre="Estación Naranjal", tipo="terminal",
                tramo="norte", orden_troncal=1, activa=True)
    base.update(overrides)
    return EstacionCrear(**base)


@pytest.fixture
def ruta(db_session) -> Ruta:
    r = Ruta(codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
             hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True)
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return r


# ── crear / codigo_existe / listar ─────────────────────────
def test_crear_estacion(db_session):
    est = estacion_service.crear_estacion(db_session, _datos())
    assert est.id is not None
    assert est.codigo == "EST-001"


def test_codigo_existe(db_session):
    estacion_service.crear_estacion(db_session, _datos())
    assert estacion_service.codigo_existe(db_session, "EST-001") is True
    assert estacion_service.codigo_existe(db_session, "EST-999") is False


def test_listar_filtra_por_tramo_y_tipo(db_session):
    estacion_service.crear_estacion(db_session, _datos(codigo="EST-001", tramo="norte", tipo="terminal"))
    estacion_service.crear_estacion(db_session, _datos(codigo="EST-002", tramo="sur", tipo="intermedia", orden_troncal=2))
    assert len(estacion_service.listar_estaciones(db_session)) == 2
    assert len(estacion_service.listar_estaciones(db_session, tramo="norte")) == 1
    assert len(estacion_service.listar_estaciones(db_session, tipo="intermedia")) == 1


def test_obtener_existente_y_none(db_session):
    est = estacion_service.crear_estacion(db_session, _datos())
    assert estacion_service.obtener_estacion(db_session, est.id).codigo == "EST-001"
    assert estacion_service.obtener_estacion(db_session, 999) is None


# ── asignar_a_ruta (alta y upsert) ─────────────────────────
def test_asignar_estacion_a_ruta(db_session, ruta):
    est = estacion_service.crear_estacion(db_session, _datos())
    recorrido = estacion_service.asignar_a_ruta(
        db_session, ruta.id, RutaEstacionAsignar(estacion_id=est.id, orden=1, tiempo_est_min=5))
    assert len(recorrido) == 1
    assert recorrido[0]["codigo"] == "EST-001"
    assert recorrido[0]["orden"] == 1


def test_asignar_actualiza_orden_existente(db_session, ruta):
    est = estacion_service.crear_estacion(db_session, _datos())
    estacion_service.asignar_a_ruta(
        db_session, ruta.id, RutaEstacionAsignar(estacion_id=est.id, orden=1, tiempo_est_min=5))
    # re-asignar la misma estación actualiza orden/tiempo (upsert)
    recorrido = estacion_service.asignar_a_ruta(
        db_session, ruta.id, RutaEstacionAsignar(estacion_id=est.id, orden=3, tiempo_est_min=9))
    assert len(recorrido) == 1
    assert recorrido[0]["orden"] == 3
    assert recorrido[0]["tiempo_est_min"] == 9


# ── desasignar_de_ruta ─────────────────────────────────────
def test_desasignar_de_ruta(db_session, ruta):
    est = estacion_service.crear_estacion(db_session, _datos())
    estacion_service.asignar_a_ruta(
        db_session, ruta.id, RutaEstacionAsignar(estacion_id=est.id, orden=1))
    assert estacion_service.desasignar_de_ruta(db_session, ruta.id, est.id) is True
    assert estacion_service.desasignar_de_ruta(db_session, ruta.id, est.id) is False
    assert estacion_service.estaciones_de_ruta(db_session, ruta.id) == []
