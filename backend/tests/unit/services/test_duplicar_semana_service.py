"""Unit tests para app.services.duplicar_semana_service (RF03 — Prototype)."""
from datetime import date, time, timedelta

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.services import duplicar_semana_service
from app.services.duplicar_semana_service import DuplicarSemanaError

ORIGEN = date(2026, 6, 1)
DESTINO = date(2026, 6, 8)


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
        nombre="Semana 1", fecha_inicio=ORIGEN, fecha_fin=date(2026, 6, 14),
        estado="borrador", creado_por=usuario_admin.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _horario(db_session, programacion, ruta, *, fecha=ORIGEN, hora=time(8, 0), dur=120):
    h = HorarioServicio(
        programacion_id=programacion.id, ruta_id=ruta.id, fecha=fecha,
        hora_salida=hora, turno="manana", duracion_est_min=dur, activo=True)
    db_session.add(h)
    db_session.commit()
    db_session.refresh(h)
    return h


def _asignar(db_session, horario, chofer, usuario_admin, area_norte):
    a = Asignacion(horario_id=horario.id, chofer_id=chofer.id, area_id=area_norte.id,
                   estado="confirmada", asignado_por=usuario_admin.id)
    db_session.add(a)
    db_session.commit()
    return a


# ── errores de dominio ─────────────────────────────────────
def test_misma_semana_lanza_error(db_session, programacion, ruta, usuario_admin):
    with pytest.raises(DuplicarSemanaError, match="distinta"):
        duplicar_semana_service.duplicar_semana(
            db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=ORIGEN,
            asignado_por=usuario_admin.id)


def test_sin_horarios_origen_lanza_error(db_session, programacion, usuario_admin):
    with pytest.raises(DuplicarSemanaError, match="No hay horarios"):
        duplicar_semana_service.duplicar_semana(
            db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
            programacion_id=programacion.id, asignado_por=usuario_admin.id)


# ── caso feliz ─────────────────────────────────────────────
def test_duplica_horarios_y_asignaciones(db_session, programacion, ruta, chofer_norte,
                                         usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta)
    _asignar(db_session, h, chofer_norte, usuario_admin, area_norte)
    res = duplicar_semana_service.duplicar_semana(
        db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
        programacion_id=programacion.id, asignado_por=usuario_admin.id)
    assert res["horarios_duplicados"] == 1
    assert res["asignaciones_duplicadas"] == 1
    assert res["desplazamiento_dias"] == 7
    # el nuevo horario quedó 7 días después
    nuevos = db_session.query(HorarioServicio).filter(HorarioServicio.fecha == DESTINO).all()
    assert len(nuevos) == 1


def test_omitir_existentes(db_session, programacion, ruta, usuario_admin):
    _horario(db_session, programacion, ruta)
    # ya existe el mismo horario en la semana destino
    _horario(db_session, programacion, ruta, fecha=DESTINO)
    res = duplicar_semana_service.duplicar_semana(
        db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
        programacion_id=programacion.id, incluir_asignaciones=False, asignado_por=usuario_admin.id)
    assert res["horarios_omitidos"] == 1
    assert res["horarios_duplicados"] == 0


def test_sin_asignaciones_no_copia_asignaciones(db_session, programacion, ruta, chofer_norte,
                                               usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta)
    _asignar(db_session, h, chofer_norte, usuario_admin, area_norte)
    res = duplicar_semana_service.duplicar_semana(
        db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
        programacion_id=programacion.id, incluir_asignaciones=False, asignado_por=usuario_admin.id)
    assert res["horarios_duplicados"] == 1
    assert res["asignaciones_duplicadas"] == 0


# ── advertencias de validación ─────────────────────────────
def test_advierte_solapamiento(db_session, programacion, ruta, chofer_norte,
                               usuario_admin, area_norte):
    # dos horarios origen del mismo chofer que se solapan el mismo día
    h1 = _horario(db_session, programacion, ruta, hora=time(8, 0), dur=120)
    h2 = _horario(db_session, programacion, ruta, hora=time(9, 0), dur=120)
    _asignar(db_session, h1, chofer_norte, usuario_admin, area_norte)
    _asignar(db_session, h2, chofer_norte, usuario_admin, area_norte)
    res = duplicar_semana_service.duplicar_semana(
        db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
        programacion_id=programacion.id, asignado_por=usuario_admin.id)
    assert res["horarios_duplicados"] == 2
    # la segunda asignación se omite por solapamiento
    assert res["asignaciones_duplicadas"] == 1
    assert any("solapado" in a for a in res["advertencias"])


def test_advierte_exceso_8h(db_session, programacion, ruta, chofer_norte,
                            usuario_admin, area_norte):
    # 5 turnos de 120 min no solapados = 10h en el día → excede 8h
    horas = [time(5, 0), time(7, 0), time(9, 0), time(11, 0), time(13, 0)]
    for hh in horas:
        h = _horario(db_session, programacion, ruta, hora=hh, dur=120)
        _asignar(db_session, h, chofer_norte, usuario_admin, area_norte)
    res = duplicar_semana_service.duplicar_semana(
        db_session, fecha_inicio_origen=ORIGEN, fecha_inicio_destino=DESTINO,
        programacion_id=programacion.id, asignado_por=usuario_admin.id)
    assert res["horarios_duplicados"] == 5
    assert res["asignaciones_duplicadas"] < 5
    assert any("8h" in a for a in res["advertencias"])
