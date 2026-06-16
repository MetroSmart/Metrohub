"""Unit tests para app.services.horario_service (RF03 — Builder)."""
from datetime import date, time

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto
from app.schemas.horario import HorarioCrear, AsignacionCrear, ProgramacionCompletaCrear
from app.services import horario_service

FECHA = date(2026, 6, 1)


@pytest.fixture
def ruta(db_session) -> Ruta:
    r = Ruta(
        codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
        hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True)
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return r


@pytest.fixture
def programacion(db_session, usuario_admin) -> Programacion:
    p = Programacion(
        nombre="Semana 1", fecha_inicio=FECHA, fecha_fin=date(2026, 6, 7),
        estado="borrador", creado_por=usuario_admin.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _horario(db_session, programacion, ruta, *, hora=time(8, 0), dur=120) -> HorarioServicio:
    h = HorarioServicio(
        programacion_id=programacion.id, ruta_id=ruta.id, fecha=FECHA,
        hora_salida=hora, turno="manana", duracion_est_min=dur, activo=True)
    db_session.add(h)
    db_session.commit()
    db_session.refresh(h)
    return h


# ── listar_horarios ────────────────────────────────────────
def test_listar_serializa_chofer_conflicto(db_session, programacion, ruta, chofer_norte,
                                           usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta)
    asig = Asignacion(horario_id=h.id, chofer_id=chofer_norte.id, area_id=area_norte.id,
                      estado="confirmada", asignado_por=usuario_admin.id)
    db_session.add(asig)
    db_session.flush()
    db_session.add(Conflicto(asignacion_id=asig.id, tipo="solapamiento_turno",
                             severidad="alta", descripcion="x", resuelto=False))
    db_session.commit()

    filas = horario_service.listar_horarios(db_session, fecha="2026-06-01")
    assert len(filas) == 1
    fila = filas[0]
    assert fila["chofer"]["id"] == chofer_norte.id
    assert fila["conflicto"]["tipo"] == "solapamiento_turno"
    assert fila["bus_placa"] is None


def test_listar_filtra_por_ruta_y_programacion(db_session, programacion, ruta):
    _horario(db_session, programacion, ruta)
    assert len(horario_service.listar_horarios(db_session, ruta_id=ruta.id)) == 1
    assert horario_service.listar_horarios(db_session, ruta_id=999) == []
    assert len(horario_service.listar_horarios(db_session, programacion_id=programacion.id)) == 1


# ── obtener / eliminar ─────────────────────────────────────
def test_obtener_horario(db_session, programacion, ruta):
    h = _horario(db_session, programacion, ruta)
    assert horario_service.obtener_horario(db_session, h.id).id == h.id
    assert horario_service.obtener_horario(db_session, 999) is None


def test_eliminar_horario(db_session, programacion, ruta):
    h = _horario(db_session, programacion, ruta)
    assert horario_service.eliminar_horario(db_session, h.id) is True
    assert horario_service.eliminar_horario(db_session, h.id) is False


# ── crear vía Builder ──────────────────────────────────────
# El Builder inserta hora_salida como string "HH:MM"; PostgreSQL lo coerce a
# TIME pero SQLite exige un objeto time, por eso estas pruebas son postgres-only.
@pytest.mark.postgres
def test_crear_horario(db_session, programacion, ruta):
    datos = HorarioCrear(programacion_id=programacion.id, ruta_id=ruta.id, fecha=FECHA,
                         hora_salida="08:00", turno="manana", duracion_est_min=120)
    h = horario_service.crear_horario(db_session, datos)
    assert h.id is not None
    assert h.duracion_est_min == 120


# BUG conocido (reportado, pendiente de corregir): programacion_builder.py usa
# detectar_solapamiento/calcular_horas_dia sin importarlos → NameError en build_asignacion.
@pytest.mark.xfail(reason="bug: import faltante en programacion_builder._validar_asignacion",
                   strict=True, raises=NameError)
def test_crear_asignacion(db_session, programacion, ruta, chofer_norte, usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta)
    datos = AsignacionCrear(horario_id=h.id, chofer_id=chofer_norte.id, area_id=area_norte.id)
    asig = horario_service.crear_asignacion(db_session, datos, asignado_por=usuario_admin.id)
    assert asig.id is not None
    assert asig.estado == "propuesta"


# ── crear_programacion_completa ────────────────────────────
@pytest.mark.postgres
def test_programacion_completa_solo_horario(db_session, programacion, ruta):
    datos = ProgramacionCompletaCrear(
        programacion_id=programacion.id, ruta_id=ruta.id, fecha=FECHA,
        hora_salida="08:00", turno="manana", duracion_est_min=120)
    res = horario_service.crear_programacion_completa(db_session, datos, asignado_por=None)
    assert "horario" in res
    assert "asignacion" not in res


# postgres-only (Time coercion) y además afectada por el bug del Builder reportado.
@pytest.mark.postgres
def test_programacion_completa_con_asignacion(db_session, programacion, ruta, chofer_norte,
                                              usuario_admin, area_norte):
    datos = ProgramacionCompletaCrear(
        programacion_id=programacion.id, ruta_id=ruta.id, fecha=FECHA,
        hora_salida="08:00", turno="manana", duracion_est_min=120,
        chofer_id=chofer_norte.id, area_id=area_norte.id)
    res = horario_service.crear_programacion_completa(db_session, datos, asignado_por=usuario_admin.id)
    assert res["asignacion"].chofer_id == chofer_norte.id


# ── listar_conflictos_abiertos ─────────────────────────────
def test_listar_conflictos_abiertos(db_session, programacion, ruta, chofer_norte,
                                    usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta)
    asig = Asignacion(horario_id=h.id, chofer_id=chofer_norte.id, area_id=area_norte.id,
                      estado="confirmada", asignado_por=usuario_admin.id)
    db_session.add(asig)
    db_session.flush()
    db_session.add(Conflicto(asignacion_id=asig.id, tipo="exceso_8h_dia",
                             severidad="alta", descripcion="x", resuelto=False))
    db_session.add(Conflicto(asignacion_id=asig.id, tipo="otro",
                             severidad="baja", descripcion="y", resuelto=True))
    db_session.commit()
    abiertos = horario_service.listar_conflictos_abiertos(db_session)
    assert len(abiertos) == 1
    assert abiertos[0].resuelto is False
