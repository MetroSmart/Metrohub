"""Unit tests para app.services.disponibilidad_service (RF04)."""
from datetime import date

import pytest

from app.schemas.disponibilidad import DisponibilidadCrear
from app.services import disponibilidad_service

FECHA = date(2026, 6, 1)


def _datos(**overrides) -> DisponibilidadCrear:
    base = dict(
        chofer_id=1, fecha=FECHA, hora_desde="08:00", hora_hasta="14:00",
        motivo="descanso", observaciones=None)
    base.update(overrides)
    return DisponibilidadCrear(**base)


# ── crear / listar / obtener ───────────────────────────────
def test_crear_persiste_indisponibilidad(db_session, chofer_norte, usuario_admin):
    disp = disponibilidad_service.crear(
        db_session, _datos(chofer_id=chofer_norte.id), registrado_por=usuario_admin.id)
    assert disp.id is not None
    assert str(disp.hora_desde)[:5] == "08:00"
    assert disp.motivo == "descanso"


def test_listar_filtra_por_chofer(db_session, chofer_norte, usuario_admin):
    disponibilidad_service.crear(
        db_session, _datos(chofer_id=chofer_norte.id), registrado_por=usuario_admin.id)
    todas = disponibilidad_service.listar(db_session)
    propias = disponibilidad_service.listar(db_session, chofer_id=chofer_norte.id)
    assert len(todas) == 1
    assert len(propias) == 1
    assert disponibilidad_service.listar(db_session, chofer_id=999) == []


def test_obtener_existente_y_none(db_session, chofer_norte, usuario_admin):
    disp = disponibilidad_service.crear(
        db_session, _datos(chofer_id=chofer_norte.id), registrado_por=usuario_admin.id)
    assert disponibilidad_service.obtener(db_session, disp.id).id == disp.id
    assert disponibilidad_service.obtener(db_session, 999) is None


# ── eliminar ───────────────────────────────────────────────
def test_eliminar(db_session, chofer_norte, usuario_admin):
    disp = disponibilidad_service.crear(
        db_session, _datos(chofer_id=chofer_norte.id), registrado_por=usuario_admin.id)
    assert disponibilidad_service.eliminar(db_session, disp.id) is True
    assert disponibilidad_service.eliminar(db_session, disp.id) is False


# ── chofer_disponible ──────────────────────────────────────
def test_chofer_disponible_sin_indisponibilidad(db_session, chofer_norte):
    assert disponibilidad_service.chofer_disponible(
        db_session, chofer_norte.id, "2026-06-01", "10:00") is True


def test_chofer_no_disponible_en_franja(db_session, chofer_norte, usuario_admin):
    disponibilidad_service.crear(
        db_session, _datos(chofer_id=chofer_norte.id, hora_desde="08:00", hora_hasta="14:00"),
        registrado_por=usuario_admin.id)
    # 10:00 cae dentro de 08:00-14:00
    assert disponibilidad_service.chofer_disponible(
        db_session, chofer_norte.id, "2026-06-01", "10:00") is False
    # 15:00 está fuera de la franja
    assert disponibilidad_service.chofer_disponible(
        db_session, chofer_norte.id, "2026-06-01", "15:00") is True
