"""Unit tests para app.services.chofer_service (RF04 — crítico RNF05)."""
from datetime import date, time

import pytest

from app.models.acceso_chofer import AccesoChofer
from app.models.chofer import Chofer
from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.schemas.chofer import ChoferCrear
from app.services import chofer_service


def _datos_chofer(**overrides) -> ChoferCrear:
    base = dict(
        dni="45892314",
        nombres="Roberto",
        apellidos="Castillo Vera",
        fecha_nacimiento=date(1988, 3, 12),
        telefono="999888777",
        email=None,
        area_id=1,
        numero_licencia="LIC-45892314",
        tipo_licencia="A-IIIB",
        fec_vence_licencia=date(2027, 1, 1),
        fec_vence_certif_prot=date(2027, 1, 1),
        anios_experiencia=5,
    )
    base.update(overrides)
    return ChoferCrear(**base)


# ── listar / obtener / dni_existe ──────────────────────────
def test_listar_filtra_por_area(db_session, area_norte, area_sur, chofer_norte):
    otro = Chofer(
        dni="43678912", nombres="Miguel", apellidos="Torres",
        fecha_nacimiento=date(1990, 1, 1), area_id=area_sur.id,
        numero_licencia="LIC-43678912", tipo_licencia="A-IIIB",
        fec_vence_licencia=date(2027, 1, 1), fec_vence_certif_prot=date(2027, 1, 1),
        estado="activo",
    )
    db_session.add(otro)
    db_session.commit()
    norte = chofer_service.listar_choferes(db_session, area_id=area_norte.id)
    assert {c.id for c in norte} == {chofer_norte.id}


def test_listar_filtra_por_estado(db_session, area_norte, chofer_norte):
    chofer_norte.estado = "vacaciones"
    db_session.commit()
    assert chofer_service.listar_choferes(db_session, estado="activo") == []
    assert len(chofer_service.listar_choferes(db_session, estado="vacaciones")) == 1


def test_obtener_existente_y_none(db_session, chofer_norte):
    assert chofer_service.obtener_chofer(db_session, chofer_norte.id).dni == chofer_norte.dni
    assert chofer_service.obtener_chofer(db_session, 999) is None


def test_dni_existe(db_session, chofer_norte):
    assert chofer_service.dni_existe(db_session, chofer_norte.dni) is True
    assert chofer_service.dni_existe(db_session, "00000000") is False


# ── crear_chofer ───────────────────────────────────────────
def test_crear_chofer_genera_acceso_portal(db_session, area_norte, usuario_admin):
    chofer = chofer_service.crear_chofer(db_session, _datos_chofer(), creado_por_id=usuario_admin.id)
    acceso = db_session.query(AccesoChofer).filter(AccesoChofer.chofer_id == chofer.id).first()
    assert acceso is not None
    # sin email de contacto, el login se deriva del DNI
    assert acceso.email == "45892314@metrohub.gob.pe"
    assert acceso.debe_cambiar_password is True


def test_crear_chofer_usa_email_contacto(db_session, area_norte):
    chofer = chofer_service.crear_chofer(db_session, _datos_chofer(email="rcastillo@metrohub.gob.pe"))
    acceso = db_session.query(AccesoChofer).filter(AccesoChofer.chofer_id == chofer.id).first()
    assert acceso.email == "rcastillo@metrohub.gob.pe"


def test_crear_chofer_email_duplicado_lanza_valueerror(db_session, area_norte):
    chofer_service.crear_chofer(db_session, _datos_chofer(email="dup@metrohub.gob.pe"))
    with pytest.raises(ValueError, match="Ya existe un acceso"):
        chofer_service.crear_chofer(
            db_session, _datos_chofer(dni="40000000", numero_licencia="LIC-40000000",
                                      email="dup@metrohub.gob.pe"))


# ── validar_area_supervisor ────────────────────────────────
def test_validar_area_supervisor_misma_area_ok(db_session, usuario_supervisor_norte, area_norte):
    # no lanza si el área coincide
    chofer_service.validar_area_supervisor(db_session, usuario_supervisor_norte.email, area_norte.id)


def test_validar_area_supervisor_otra_area_lanza(db_session, usuario_supervisor_norte, area_sur):
    with pytest.raises(PermissionError, match="área operativa"):
        chofer_service.validar_area_supervisor(db_session, usuario_supervisor_norte.email, area_sur.id)


# ── actualizar_estado ──────────────────────────────────────
def test_actualizar_estado_ok(db_session, chofer_norte):
    actualizado = chofer_service.actualizar_estado(db_session, chofer_norte.id, "suspendido")
    assert actualizado.estado == "suspendido"


def test_actualizar_estado_inexistente_none(db_session):
    assert chofer_service.actualizar_estado(db_session, 999, "activo") is None


# ── alertas_documentos ─────────────────────────────────────
def test_alertas_por_vencer(db_session, area_norte):
    chofer_service.crear_chofer(
        db_session,
        _datos_chofer(fec_vence_licencia=date.today().replace(year=date.today().year),
                      fec_vence_certif_prot=date.today()))
    alertas = chofer_service.alertas_documentos(db_session, dias_limite=30)
    assert len(alertas) == 1
    assert alertas[0]["estado"] in {"POR VENCER", "VENCIDA"}


def test_alertas_vencida_cuando_dias_negativos(db_session, area_norte):
    from datetime import timedelta
    ayer = date.today() - timedelta(days=5)
    chofer_service.crear_chofer(
        db_session, _datos_chofer(fec_vence_certif_prot=ayer))
    alertas = chofer_service.alertas_documentos(db_session)
    assert alertas[0]["estado"] == "VENCIDA"


def test_alertas_ignora_documentos_vigentes(db_session, area_norte):
    from datetime import timedelta
    lejano = date.today() + timedelta(days=365)
    chofer_service.crear_chofer(
        db_session, _datos_chofer(fec_vence_licencia=lejano, fec_vence_certif_prot=lejano))
    assert chofer_service.alertas_documentos(db_session) == []


# ── serializar_chofer_con_acceso ───────────────────────────
def test_serializar_incluye_acceso_portal(db_session, area_norte):
    chofer = chofer_service.crear_chofer(db_session, _datos_chofer())
    data = chofer_service.serializar_chofer_con_acceso(db_session, chofer)
    assert data["dni"] == "45892314"
    assert data["acceso_portal"]["email"] == "45892314@metrohub.gob.pe"
    assert data["acceso_portal"]["debe_cambiar_password"] is True


# ── listar_mis_asignaciones ────────────────────────────────
def test_mis_asignaciones_vacio(db_session, chofer_norte):
    res = chofer_service.listar_mis_asignaciones(db_session, chofer_norte.id, fecha="2026-06-01")
    assert res["total"] == 0
    assert res["asignaciones"] == []
    assert res["siguiente_asignacion_id"] is None


def test_mis_asignaciones_marca_siguiente(db_session, chofer_norte, usuario_admin, area_norte):
    ruta = Ruta(
        codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
        hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True)
    db_session.add(ruta)
    db_session.flush()
    prog = Programacion(
        nombre="Semana 1", fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 7),
        estado="aprobada", creado_por=usuario_admin.id)
    db_session.add(prog)
    db_session.flush()
    horario = HorarioServicio(
        programacion_id=prog.id, ruta_id=ruta.id, fecha=date(2026, 6, 1),
        hora_salida=time(8, 0), turno="manana", duracion_est_min=120, activo=True)
    db_session.add(horario)
    db_session.flush()
    db_session.add(Asignacion(
        horario_id=horario.id, chofer_id=chofer_norte.id, area_id=area_norte.id,
        estado="confirmada", asignado_por=usuario_admin.id))
    db_session.commit()

    res = chofer_service.listar_mis_asignaciones(db_session, chofer_norte.id, fecha="2026-06-01")
    assert res["total"] == 1
    assert res["asignaciones"][0]["es_siguiente"] is True
    assert res["asignaciones"][0]["ruta"]["codigo"] == "SIT-1"
