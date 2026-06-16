"""Unit tests para app.services.horario_validacion (RF03/RF04 — crítico RNF05).

Reglas de solapamiento de turnos y cálculo de horas/día de un chofer.
"""
from datetime import date, time

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.services import horario_validacion

FECHA = date(2026, 6, 1)


@pytest.fixture
def ruta(db_session) -> Ruta:
    r = Ruta(
        codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
        hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True,
    )
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return r


@pytest.fixture
def programacion(db_session, usuario_admin) -> Programacion:
    p = Programacion(
        nombre="Semana 1", fecha_inicio=FECHA, fecha_fin=date(2026, 6, 7),
        estado="borrador", creado_por=usuario_admin.id,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _horario(db_session, programacion, ruta, *, hora_salida: time, duracion_min: int) -> HorarioServicio:
    h = HorarioServicio(
        programacion_id=programacion.id, ruta_id=ruta.id, fecha=FECHA,
        hora_salida=hora_salida, turno="manana", duracion_est_min=duracion_min, activo=True,
    )
    db_session.add(h)
    db_session.commit()
    db_session.refresh(h)
    return h


def _asignacion(db_session, horario, chofer, usuario_admin, area_norte) -> Asignacion:
    a = Asignacion(
        horario_id=horario.id, chofer_id=chofer.id, area_id=area_norte.id,
        estado="confirmada", asignado_por=usuario_admin.id,
    )
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    return a


# ── detectar_solapamiento ──────────────────────────────────
def test_solapamiento_detecta_cruce(db_session, programacion, ruta, chofer_norte,
                                    usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, hora_salida=time(8, 0), duracion_min=120)
    _asignacion(db_session, h, chofer_norte, usuario_admin, area_norte)
    # nuevo turno 09:00-10:00 cruza con 08:00-10:00
    assert horario_validacion.detectar_solapamiento(
        db_session, chofer_norte.id, FECHA, "09:00", 60) is True


def test_solapamiento_falso_cuando_contiguos(db_session, programacion, ruta, chofer_norte,
                                             usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, hora_salida=time(8, 0), duracion_min=120)
    _asignacion(db_session, h, chofer_norte, usuario_admin, area_norte)
    # nuevo turno 10:00-11:00 empieza justo cuando termina el otro
    assert horario_validacion.detectar_solapamiento(
        db_session, chofer_norte.id, FECHA, "10:00", 60) is False


def test_solapamiento_falso_otra_fecha(db_session, programacion, ruta, chofer_norte,
                                       usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, hora_salida=time(8, 0), duracion_min=120)
    _asignacion(db_session, h, chofer_norte, usuario_admin, area_norte)
    assert horario_validacion.detectar_solapamiento(
        db_session, chofer_norte.id, date(2026, 6, 2), "08:00", 120) is False


def test_solapamiento_excluye_asignacion_propia(db_session, programacion, ruta, chofer_norte,
                                                usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, hora_salida=time(8, 0), duracion_min=120)
    asig = _asignacion(db_session, h, chofer_norte, usuario_admin, area_norte)
    # al editar la misma asignación se excluye y no debe reportar solape consigo misma
    assert horario_validacion.detectar_solapamiento(
        db_session, chofer_norte.id, FECHA, "08:00", 120, excluir_asig_id=asig.id) is False


# ── calcular_horas_dia ─────────────────────────────────────
def test_calcular_horas_suma_existentes_mas_nuevo(db_session, programacion, ruta, chofer_norte,
                                                  usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, hora_salida=time(8, 0), duracion_min=120)
    _asignacion(db_session, h, chofer_norte, usuario_admin, area_norte)
    # 120 existentes + 120 nuevos = 240 min = 4 h
    assert horario_validacion.calcular_horas_dia(db_session, chofer_norte.id, FECHA, 120) == 4


def test_calcular_horas_sin_asignaciones_previas(db_session, chofer_norte):
    # sin asignaciones, solo cuenta la duración nueva
    assert horario_validacion.calcular_horas_dia(db_session, chofer_norte.id, FECHA, 180) == 3
