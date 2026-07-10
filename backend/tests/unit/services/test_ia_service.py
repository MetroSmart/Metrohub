"""Unit tests para app.services.ia_service (RF05 — Copiloto IA).

Cubre las funciones puras (candidatos, noches consecutivas), la detección de
alertas de fatiga y la construcción de contexto para el chat. Las fechas se
siembran relativas a date.today() porque detectar_alertas_fatiga y los _ctx_*
trabajan sobre la semana en curso.
"""
from datetime import date, time, timedelta

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.chofer import Chofer
from app.models.disponibilidad_chofer import DisponibilidadChofer
from app.services import ia_service

HOY   = date.today()
LUNES = HOY - timedelta(days=HOY.weekday())


# ── Fixtures / helpers de siembra ─────────────────────────
@pytest.fixture
def ruta(db_session) -> Ruta:
    r = Ruta(codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
             hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True)
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return r


@pytest.fixture
def programacion(db_session, usuario_admin) -> Programacion:
    p = Programacion(nombre="Semana IA", fecha_inicio=LUNES,
                     fecha_fin=LUNES + timedelta(days=6),
                     estado="borrador", creado_por=usuario_admin.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def chofer_b(db_session, area_norte) -> Chofer:
    c = Chofer(dni="45123456", nombres="Rosa", apellidos="Quispe Mamani",
               fecha_nacimiento=date(1990, 3, 15), area_id=area_norte.id,
               numero_licencia="LIC-45123456", tipo_licencia="A-IIIB",
               fec_vence_licencia=date(2027, 1, 1), fec_vence_certif_prot=date(2027, 1, 1),
               estado="activo")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def _horario(db, programacion, ruta, *, fecha, hora=time(8, 0), dur=120,
             turno="manana") -> HorarioServicio:
    h = HorarioServicio(programacion_id=programacion.id, ruta_id=ruta.id, fecha=fecha,
                        hora_salida=hora, turno=turno, duracion_est_min=dur, activo=True)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def _asignar(db, horario, chofer, area, admin, estado="confirmada") -> Asignacion:
    a = Asignacion(horario_id=horario.id, chofer_id=chofer.id, area_id=area.id,
                   estado=estado, asignado_por=admin.id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


class _FakeAsig:
    """Asignación mínima para _max_consecutivos_noche (solo usa .horario.fecha)."""
    class _H:
        def __init__(self, fecha):
            self.fecha = fecha

    def __init__(self, fecha):
        self.horario = self._H(fecha)


# ── Funciones puras ───────────────────────────────────────
def test_ids_candidatos_validos():
    datos = {"candidatos": [{"chofer_id": 1}, {"chofer_id": 7}]}
    assert ia_service.ids_candidatos_validos(datos) == {1, 7}
    assert ia_service.ids_candidatos_validos({}) == set()


def test_mejor_candidato_deterministico_elige_menor_carga():
    datos = {"candidatos": [
        {"chofer_id": 1, "horas_semana": 30.0, "turnos_noche_consecutivos": 0},
        {"chofer_id": 2, "horas_semana": 12.0, "turnos_noche_consecutivos": 2},
        {"chofer_id": 3, "horas_semana": 12.0, "turnos_noche_consecutivos": 0},
    ]}
    assert ia_service.mejor_candidato_deterministico(datos)["chofer_id"] == 3


def test_mejor_candidato_deterministico_sin_candidatos():
    assert ia_service.mejor_candidato_deterministico({"candidatos": []}) is None
    assert ia_service.mejor_candidato_deterministico({}) is None


def test_max_consecutivos_noche():
    assert ia_service._max_consecutivos_noche([]) == 0
    assert ia_service._max_consecutivos_noche([_FakeAsig(LUNES)]) == 1
    # 3 seguidas, hueco, 2 seguidas → máximo 3
    fechas = [LUNES, LUNES + timedelta(days=1), LUNES + timedelta(days=2),
              LUNES + timedelta(days=4), LUNES + timedelta(days=5)]
    assert ia_service._max_consecutivos_noche([_FakeAsig(f) for f in fechas]) == 3


# ── detectar_alertas_fatiga ───────────────────────────────
def test_sin_asignaciones_no_hay_alertas(db_session):
    assert ia_service.detectar_alertas_fatiga(db_session) == []


def test_alerta_exceso_horas_semana(db_session, programacion, ruta, chofer_norte,
                                    usuario_admin, area_norte):
    # 7 días × 2 turnos de 4 h = 56 h > 48 h (duración máx. por turno: 240 min).
    # Gaps de exactamente 8 h entre turnos → no dispara alerta de descanso.
    for i in range(7):
        fecha = LUNES + timedelta(days=i)
        h1 = _horario(db_session, programacion, ruta, fecha=fecha, hora=time(6, 0), dur=240)
        h2 = _horario(db_session, programacion, ruta, fecha=fecha, hora=time(18, 0),
                      dur=240, turno="tarde")
        _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
        _asignar(db_session, h2, chofer_norte, area_norte, usuario_admin)

    alertas = ia_service.detectar_alertas_fatiga(db_session)
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "exceso_horas_semana"
    assert alertas[0]["chofer_id"] == chofer_norte.id
    assert alertas[0]["detalle"]["horas_asignadas"] == 56.0


def test_alerta_turnos_noche_consecutivos(db_session, programacion, ruta, chofer_norte,
                                          usuario_admin, area_norte):
    # 4 noches seguidas (límite 3), 4 h c/u → 16 h (no excede semana)
    for i in range(4):
        h = _horario(db_session, programacion, ruta, fecha=LUNES + timedelta(days=i),
                     hora=time(22, 0), dur=240, turno="noche")
        _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)

    alertas = ia_service.detectar_alertas_fatiga(db_session)
    tipos = [a["tipo"] for a in alertas]
    assert "turnos_noche_consecutivos" in tipos
    alerta = next(a for a in alertas if a["tipo"] == "turnos_noche_consecutivos")
    assert alerta["detalle"]["turnos_consecutivos"] == 4


def test_alerta_descanso_insuficiente(db_session, programacion, ruta, chofer_norte,
                                      usuario_admin, area_norte):
    # Mismo día: 06:00-08:00 y 10:00-12:00 → gap 2 h < 8 h
    h1 = _horario(db_session, programacion, ruta, fecha=LUNES, hora=time(6, 0), dur=120)
    h2 = _horario(db_session, programacion, ruta, fecha=LUNES, hora=time(10, 0), dur=120)
    _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    _asignar(db_session, h2, chofer_norte, area_norte, usuario_admin)

    alertas = ia_service.detectar_alertas_fatiga(db_session)
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "descanso_insuficiente"
    assert alertas[0]["detalle"]["descanso_horas"] == 2.0


def test_alerta_se_excluye_si_ya_hay_descanso_registrado(db_session, programacion, ruta,
                                                         chofer_norte, usuario_admin,
                                                         area_norte):
    h1 = _horario(db_session, programacion, ruta, fecha=LUNES, hora=time(6, 0), dur=120)
    h2 = _horario(db_session, programacion, ruta, fecha=LUNES, hora=time(10, 0), dur=120)
    _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    _asignar(db_session, h2, chofer_norte, area_norte, usuario_admin)
    db_session.add(DisponibilidadChofer(
        chofer_id=chofer_norte.id, fecha=LUNES, hora_desde=time(0, 0),
        hora_hasta=time(23, 59), motivo="descanso", observaciones="x",
        registrado_por=usuario_admin.id))
    db_session.commit()

    assert ia_service.detectar_alertas_fatiga(db_session) == []


# ── obtener_candidatos_reemplazo ──────────────────────────
def test_candidatos_reemplazo_asignacion_inexistente(db_session):
    assert ia_service.obtener_candidatos_reemplazo(db_session, 999) == {}


def test_candidatos_reemplazo_incluye_chofer_libre(db_session, programacion, ruta,
                                                   chofer_norte, chofer_b,
                                                   usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, fecha=LUNES)
    asig = _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)

    datos = ia_service.obtener_candidatos_reemplazo(db_session, asig.id)
    assert datos["chofer_ausente"]["nombres"] == chofer_norte.nombres
    assert datos["horario"]["turno"] == "manana"
    ids = {c["chofer_id"] for c in datos["candidatos"]}
    assert ids == {chofer_b.id}          # el ausente no se propone a sí mismo


def test_candidatos_reemplazo_excluye_ocupado_y_bloqueado(db_session, programacion, ruta,
                                                          chofer_norte, chofer_b,
                                                          usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, fecha=LUNES)
    asig = _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)
    # chofer_b bloqueado todo el día por disponibilidad
    db_session.add(DisponibilidadChofer(
        chofer_id=chofer_b.id, fecha=LUNES, hora_desde=time(0, 0),
        hora_hasta=time(23, 59), motivo="descanso", observaciones="x",
        registrado_por=usuario_admin.id))
    db_session.commit()

    datos = ia_service.obtener_candidatos_reemplazo(db_session, asig.id)
    assert datos["candidatos"] == []


# ── obtener_contexto_chat ─────────────────────────────────
def test_ctx_intent_no_reconocido(db_session):
    assert ia_service.obtener_contexto_chat(db_session, "otro", {}) == {
        "info": "intent no reconocido"}


def test_ctx_resolver_conflicto(db_session):
    ctx = ia_service.obtener_contexto_chat(
        db_session, "resolver_conflicto",
        {"tipo": "solapamiento_turno", "severidad": "alta", "descripcion": "d"})
    assert ctx == {"tipo": "solapamiento_turno", "severidad": "alta", "descripcion": "d"}


def test_ctx_disponibilidad_lista_choferes_libres(db_session, programacion, ruta,
                                                  chofer_norte, chofer_b,
                                                  usuario_admin, area_norte):
    # chofer_norte ocupado hoy; chofer_b libre
    h = _horario(db_session, programacion, ruta, fecha=HOY)
    _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)

    ctx = ia_service.obtener_contexto_chat(db_session, "disponibilidad", {"fecha": str(HOY)})
    assert ctx["total_disponibles"] == 1
    assert "Rosa" in ctx["choferes"]


def test_ctx_explicar_alerta_sin_alertas(db_session):
    ctx = ia_service.obtener_contexto_chat(db_session, "explicar_alerta", {})
    assert "info" in ctx


def test_ctx_horas_area(db_session, programacion, ruta, chofer_norte,
                        usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, fecha=LUNES, dur=120)
    _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)

    ctx = ia_service.obtener_contexto_chat(db_session, "horas_area", {})
    fila = next(a for a in ctx["areas"] if a["area"] == area_norte.nombre)
    assert fila["horas_asignadas"] == 2.0
    assert fila["total_asignaciones"] == 1


def test_ctx_estado_programacion(db_session, programacion):
    ctx = ia_service.obtener_contexto_chat(db_session, "estado_programacion", {})
    assert ctx["programaciones"][0]["nombre"] == "Semana IA"


def test_ctx_estado_programacion_vacio(db_session):
    ctx = ia_service.obtener_contexto_chat(db_session, "estado_programacion", {})
    assert ctx == {"info": "No hay programaciones registradas."}
