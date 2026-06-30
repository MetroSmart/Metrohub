"""Unit tests para app.services.conflicto_service (RF03 — crítico RNF05).

Listado de conflictos (filtro por resuelto) y resolución.
"""
from datetime import date, time

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto
from app.services import conflicto_service

FECHA = date(2026, 6, 1)


@pytest.fixture
def asignacion(db_session, usuario_admin, area_norte, chofer_norte) -> Asignacion:
    ruta = Ruta(
        codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
        hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True,
    )
    db_session.add(ruta)
    db_session.flush()
    prog = Programacion(
        nombre="Semana 1", fecha_inicio=FECHA, fecha_fin=date(2026, 6, 7),
        estado="borrador", creado_por=usuario_admin.id,
    )
    db_session.add(prog)
    db_session.flush()
    horario = HorarioServicio(
        programacion_id=prog.id, ruta_id=ruta.id, fecha=FECHA,
        hora_salida=time(8, 0), turno="manana", duracion_est_min=120, activo=True,
    )
    db_session.add(horario)
    db_session.flush()
    asig = Asignacion(
        horario_id=horario.id, chofer_id=chofer_norte.id, area_id=area_norte.id,
        estado="propuesta", asignado_por=usuario_admin.id,
    )
    db_session.add(asig)
    db_session.commit()
    db_session.refresh(asig)
    return asig


def _conflicto(db_session, asignacion, *, resuelto: bool, tipo="solapamiento_turno") -> Conflicto:
    c = Conflicto(
        asignacion_id=asignacion.id, tipo=tipo, severidad="alta",
        descripcion="Turno solapado", resuelto=resuelto,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


# ── listar_conflictos ──────────────────────────────────────
def test_listar_todos(db_session, asignacion):
    _conflicto(db_session, asignacion, resuelto=False)
    _conflicto(db_session, asignacion, resuelto=True, tipo="exceso_8h_dia")
    assert len(conflicto_service.listar_conflictos(db_session)) == 2


def test_listar_solo_pendientes(db_session, asignacion):
    _conflicto(db_session, asignacion, resuelto=False)
    _conflicto(db_session, asignacion, resuelto=True, tipo="exceso_8h_dia")
    pendientes = conflicto_service.listar_conflictos(db_session, resuelto=False)
    assert len(pendientes) == 1
    assert pendientes[0].resuelto is False


def test_listar_solo_resueltos(db_session, asignacion):
    _conflicto(db_session, asignacion, resuelto=False)
    _conflicto(db_session, asignacion, resuelto=True, tipo="exceso_8h_dia")
    resueltos = conflicto_service.listar_conflictos(db_session, resuelto=True)
    assert len(resueltos) == 1
    assert resueltos[0].resuelto is True


# ── resolver_conflicto ─────────────────────────────────────
def test_resolver_marca_resuelto(db_session, asignacion, usuario_admin):
    c = _conflicto(db_session, asignacion, resuelto=False)
    resuelto = conflicto_service.resolver_conflicto(db_session, c.id, usuario_admin.id)
    assert resuelto is not None
    assert resuelto.resuelto is True
    assert resuelto.resuelto_por == usuario_admin.id
    assert resuelto.fecha_resolucion is not None


def test_resolver_inexistente_devuelve_none(db_session, usuario_admin):
    assert conflicto_service.resolver_conflicto(db_session, 999, usuario_admin.id) is None
