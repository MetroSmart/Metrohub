"""Pruebas de integración de /api/ia/* (RF05 — Copiloto IA).

El servicio IA externo (Groq) NUNCA se llama: se hace monkeypatch de
app.routers.ia._llamar_ia con un stub async que devuelve respuestas fijas y
cuenta las llamadas (para verificar el cache). El cache de módulo se limpia
entre tests con una fixture autouse.

Las fechas se siembran relativas a date.today() porque el selector filtra
hoy..hoy+14 y las alertas de fatiga trabajan sobre la semana en curso.
"""
from datetime import date, time, timedelta

import pytest

import app.routers.ia as ia_router
from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.chofer import Chofer
from app.models.conflicto import Conflicto
from app.models.disponibilidad_chofer import DisponibilidadChofer

HOY    = date.today()
LUNES  = HOY - timedelta(days=HOY.weekday())
MANANA = HOY + timedelta(days=1)


# ── Infraestructura de mocking ────────────────────────────
@pytest.fixture(autouse=True)
def limpiar_cache_ia():
    ia_router._cache.clear()
    yield
    ia_router._cache.clear()


@pytest.fixture
def mock_ia(monkeypatch):
    """Stub de _llamar_ia. `estado['recomendar']` controla el chofer sugerido."""
    estado = {"llamadas": 0, "recomendar": None}

    async def _fake_llamar_ia(path: str, payload: dict) -> dict:
        estado["llamadas"] += 1
        if path == "/reemplazo":
            return {"chofer_id_recomendado": estado["recomendar"],
                    "recomendacion": "Recomendación simulada por el mock."}
        if path == "/alertas-fatiga":
            return {"alertas": [
                {"alerta": "Alerta simulada", "sugerencia": "Descansar", "severidad": "media"}
                for _ in payload.get("alertas", [])
            ]}
        if path == "/chat":
            return {"respuesta": "Respuesta simulada del asistente."}
        return {}

    monkeypatch.setattr(ia_router, "_llamar_ia", _fake_llamar_ia)
    return estado


# ── Fixtures de datos ─────────────────────────────────────
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
                     fecha_fin=LUNES + timedelta(days=13),
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


@pytest.fixture
def chofer_sur(db_session, area_sur) -> Chofer:
    c = Chofer(dni="46789012", nombres="Pedro", apellidos="Salas Ríos",
               fecha_nacimiento=date(1988, 7, 20), area_id=area_sur.id,
               numero_licencia="LIC-46789012", tipo_licencia="A-IIIB",
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


def _asignar(db, horario, chofer, area, admin, estado="propuesta") -> Asignacion:
    a = Asignacion(horario_id=horario.id, chofer_id=chofer.id, area_id=area.id,
                   estado=estado, asignado_por=admin.id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _conflicto(db, asignacion, *, tipo="solapamiento_turno") -> Conflicto:
    c = Conflicto(asignacion_id=asignacion.id, tipo=tipo, severidad="alta",
                  descripcion="conflicto de prueba", resuelto=False)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def asignacion_manana(db_session, programacion, ruta, chofer_norte, usuario_admin,
                      area_norte) -> Asignacion:
    """Asignación 'propuesta' para mañana con chofer_norte (área norte)."""
    h = _horario(db_session, programacion, ruta, fecha=MANANA)
    return _asignar(db_session, h, chofer_norte, area_norte, usuario_admin)


# ── GET /api/ia/health ────────────────────────────────────
def test_health_responde_aunque_ia_este_caida(client, monkeypatch):
    monkeypatch.setattr(ia_router, "IA_SERVICE_URL", "http://localhost:1")  # puerto cerrado
    resp = client.get("/api/ia/health")
    assert resp.status_code == 200
    assert resp.json()["ia_service"] == "no disponible"


# ── GET /api/ia/asignaciones-selector ─────────────────────
def test_selector_chofer_403(client, auth_chofer_headers):
    assert client.get("/api/ia/asignaciones-selector",
                      headers=auth_chofer_headers).status_code == 403


def test_selector_admin_prioriza_problemas(client, auth_admin_headers, db_session,
                                           programacion, ruta, chofer_norte, chofer_b,
                                           usuario_admin, area_norte):
    h1 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(8, 0))
    h2 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(14, 0), turno="tarde")
    _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    asig_con_conflicto = _asignar(db_session, h2, chofer_b, area_norte, usuario_admin)
    _conflicto(db_session, asig_con_conflicto)

    resp = client.get("/api/ia/asignaciones-selector", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert body[0]["asignacion_id"] == asig_con_conflicto.id
    assert body[0]["tiene_problema"] is True
    assert body[1]["tiene_problema"] is False


def test_selector_supervisor_solo_su_area(client, auth_supervisor_norte_headers, db_session,
                                          programacion, ruta, chofer_norte, chofer_sur,
                                          usuario_admin, area_norte, area_sur):
    h1 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(8, 0))
    h2 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(14, 0), turno="tarde")
    asig_norte = _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    _asignar(db_session, h2, chofer_sur, area_sur, usuario_admin)

    resp = client.get("/api/ia/asignaciones-selector",
                      headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert [a["asignacion_id"] for a in body] == [asig_norte.id]


# ── POST /api/ia/sugerir-reemplazo/{id} ───────────────────
def test_sugerir_reemplazo_404_asignacion(client, auth_admin_headers, mock_ia):
    resp = client.post("/api/ia/sugerir-reemplazo/999", headers=auth_admin_headers)
    assert resp.status_code == 404


def test_sugerir_reemplazo_404_sin_candidatos(client, auth_admin_headers, mock_ia,
                                              asignacion_manana):
    # chofer_norte es el único chofer → no hay candidatos
    resp = client.post(f"/api/ia/sugerir-reemplazo/{asignacion_manana.id}",
                       headers=auth_admin_headers)
    assert resp.status_code == 404
    assert "candidatos" in resp.json()["detail"]


def test_sugerir_reemplazo_ok_y_cachea(client, auth_admin_headers, mock_ia,
                                       asignacion_manana, chofer_b):
    mock_ia["recomendar"] = chofer_b.id

    resp = client.post(f"/api/ia/sugerir-reemplazo/{asignacion_manana.id}",
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["recomendacion_ia"]["chofer_id_recomendado"] == chofer_b.id
    assert body["candidatos_evaluados"] == 1
    assert mock_ia["llamadas"] == 1

    # segunda llamada sale del cache: el stub no vuelve a invocarse
    resp2 = client.post(f"/api/ia/sugerir-reemplazo/{asignacion_manana.id}",
                        headers=auth_admin_headers)
    assert resp2.status_code == 200
    assert mock_ia["llamadas"] == 1


def test_sugerir_reemplazo_supervisor_otra_area_403(client, auth_supervisor_norte_headers,
                                                    mock_ia, db_session, programacion, ruta,
                                                    chofer_sur, usuario_admin, area_sur):
    h = _horario(db_session, programacion, ruta, fecha=MANANA)
    asig = _asignar(db_session, h, chofer_sur, area_sur, usuario_admin)
    resp = client.post(f"/api/ia/sugerir-reemplazo/{asig.id}",
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


# ── GET /api/ia/alertas-fatiga ────────────────────────────
def test_alertas_fatiga_chofer_403(client, auth_chofer_headers):
    assert client.get("/api/ia/alertas-fatiga",
                      headers=auth_chofer_headers).status_code == 403


def test_alertas_fatiga_sin_alertas(client, auth_admin_headers, mock_ia):
    resp = client.get("/api/ia/alertas-fatiga", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert mock_ia["llamadas"] == 0  # sin alertas no se consulta la IA


def _sembrar_descanso_insuficiente(db, programacion, ruta, chofer, area, admin):
    """Dos turnos el mismo día con gap de 2 h < 8 h → alerta de fatiga."""
    h1 = _horario(db, programacion, ruta, fecha=LUNES, hora=time(6, 0))
    h2 = _horario(db, programacion, ruta, fecha=LUNES, hora=time(10, 0))
    _asignar(db, h1, chofer, area, admin, estado="confirmada")
    _asignar(db, h2, chofer, area, admin, estado="confirmada")


def test_alertas_fatiga_merge_ia_y_cache(client, auth_admin_headers, mock_ia, db_session,
                                         programacion, ruta, chofer_norte, usuario_admin,
                                         area_norte):
    _sembrar_descanso_insuficiente(db_session, programacion, ruta, chofer_norte,
                                   area_norte, usuario_admin)

    resp = client.get("/api/ia/alertas-fatiga", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    alerta = body["alertas"][0]
    # merge de la respuesta IA con los datos crudos
    assert alerta["alerta"] == "Alerta simulada"
    assert alerta["chofer_id"] == chofer_norte.id
    assert alerta["tipo"] == "descanso_insuficiente"
    assert mock_ia["llamadas"] == 1

    # cache: segunda llamada sin force no consulta la IA; con force sí
    client.get("/api/ia/alertas-fatiga", headers=auth_admin_headers)
    assert mock_ia["llamadas"] == 1
    client.get("/api/ia/alertas-fatiga?force=true", headers=auth_admin_headers)
    assert mock_ia["llamadas"] == 2


def test_alertas_fatiga_supervisor_filtra_area(client, auth_supervisor_norte_headers,
                                               mock_ia, db_session, programacion, ruta,
                                               chofer_sur, usuario_admin, area_sur,
                                               usuario_supervisor_norte):
    # la única alerta es de un chofer del área sur → supervisor norte no la ve
    _sembrar_descanso_insuficiente(db_session, programacion, ruta, chofer_sur,
                                   area_sur, usuario_admin)

    resp = client.get("/api/ia/alertas-fatiga", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# ── POST /api/ia/chat ─────────────────────────────────────
def test_chat_intent_invalido_400(client, auth_admin_headers, mock_ia):
    resp = client.post("/api/ia/chat",
                       json={"intent": "hackear", "pregunta": "¿?"},
                       headers=auth_admin_headers)
    assert resp.status_code == 400


def test_chat_pregunta_vacia_400(client, auth_admin_headers, mock_ia):
    resp = client.post("/api/ia/chat",
                       json={"intent": "disponibilidad", "pregunta": ""},
                       headers=auth_admin_headers)
    assert resp.status_code == 400


def test_chat_ok(client, auth_admin_headers, mock_ia):
    resp = client.post("/api/ia/chat",
                       json={"intent": "disponibilidad",
                             "pregunta": "¿Quién está libre mañana?"},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "disponibilidad"
    assert body["respuesta"] == "Respuesta simulada del asistente."


def test_chat_resolver_conflicto_usa_cache(client, auth_admin_headers, mock_ia):
    payload = {"intent": "resolver_conflicto", "pregunta": "¿Cómo lo resuelvo?",
               "params": {"tipo": "solapamiento_turno", "severidad": "alta"}}
    assert client.post("/api/ia/chat", json=payload,
                       headers=auth_admin_headers).status_code == 200
    assert mock_ia["llamadas"] == 1
    assert client.post("/api/ia/chat", json=payload,
                       headers=auth_admin_headers).status_code == 200
    assert mock_ia["llamadas"] == 1  # respondió desde cache


# ── POST /api/ia/aplicar-reemplazo/{id} ───────────────────
def test_aplicar_reemplazo_flujo_completo(client, auth_admin_headers, mock_ia, db_session,
                                          asignacion_manana, chofer_b, chofer_norte):
    conflicto = _conflicto(db_session, asignacion_manana)
    mock_ia["recomendar"] = chofer_b.id

    resp = client.post(f"/api/ia/aplicar-reemplazo/{asignacion_manana.id}",
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["chofer_reemplazo"]["id"] == chofer_b.id

    db_session.expire_all()
    asig_old = db_session.get(Asignacion, asignacion_manana.id)
    asig_nueva = db_session.get(Asignacion, body["asignacion_nueva_id"])
    assert asig_old.estado == "reemplazada"
    assert asig_nueva.estado == "confirmada"
    assert asig_nueva.chofer_id == chofer_b.id
    assert asig_nueva.horario_id == asig_old.horario_id
    assert db_session.get(Conflicto, conflicto.id).resuelto is True


def test_aplicar_reemplazo_fallback_deterministico(client, auth_admin_headers, mock_ia,
                                                   db_session, asignacion_manana, chofer_b):
    # la IA recomienda un chofer que no es candidato → se usa el determinístico
    mock_ia["recomendar"] = 9999

    resp = client.post(f"/api/ia/aplicar-reemplazo/{asignacion_manana.id}",
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["chofer_reemplazo"]["id"] == chofer_b.id


def test_aplicar_reemplazo_estado_no_activo_400(client, auth_admin_headers, mock_ia,
                                                db_session, programacion, ruta,
                                                chofer_norte, usuario_admin, area_norte):
    h = _horario(db_session, programacion, ruta, fecha=MANANA)
    asig = _asignar(db_session, h, chofer_norte, area_norte, usuario_admin,
                    estado="cancelada")
    resp = client.post(f"/api/ia/aplicar-reemplazo/{asig.id}", headers=auth_admin_headers)
    assert resp.status_code == 400


def test_aplicar_reemplazo_sin_candidatos_404(client, auth_admin_headers, mock_ia,
                                              asignacion_manana):
    resp = client.post(f"/api/ia/aplicar-reemplazo/{asignacion_manana.id}",
                       headers=auth_admin_headers)
    assert resp.status_code == 404


# ── POST /api/ia/programar-descanso/{chofer_id} ───────────
def test_programar_descanso_libera_turnos(client, auth_admin_headers, db_session,
                                          asignacion_manana, chofer_norte):
    resp = client.post(f"/api/ia/programar-descanso/{chofer_norte.id}",
                       json={"fecha": str(MANANA), "observaciones": "fatiga"},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["turnos_liberados"] == 1

    db_session.expire_all()
    assert db_session.get(Asignacion, asignacion_manana.id).estado == "cancelada"
    disp = (db_session.query(DisponibilidadChofer)
            .filter(DisponibilidadChofer.chofer_id == chofer_norte.id,
                    DisponibilidadChofer.fecha == MANANA)
            .first())
    assert disp is not None
    assert disp.motivo == "descanso"


def test_programar_descanso_supervisor_otra_area_403(client, auth_supervisor_norte_headers,
                                                     chofer_sur):
    resp = client.post(f"/api/ia/programar-descanso/{chofer_sur.id}",
                       json={"fecha": str(MANANA)},
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


# ── POST /api/ia/confirmar-dia ────────────────────────────
def test_confirmar_dia_omite_conflictivas(client, auth_admin_headers, db_session,
                                          programacion, ruta, chofer_norte, chofer_b,
                                          usuario_admin, area_norte):
    h1 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(8, 0))
    h2 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(14, 0), turno="tarde")
    asig_limpia = _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    asig_conflictiva = _asignar(db_session, h2, chofer_b, area_norte, usuario_admin)
    _conflicto(db_session, asig_conflictiva)

    resp = client.post("/api/ia/confirmar-dia", json={"fecha": str(MANANA)},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmadas"] == 1
    assert body["omitidas"] == 1
    assert body["detalles_omitidas"][0]["asignacion_id"] == asig_conflictiva.id

    db_session.expire_all()
    assert db_session.get(Asignacion, asig_limpia.id).estado == "confirmada"
    assert db_session.get(Asignacion, asig_conflictiva.id).estado == "propuesta"


def test_confirmar_dia_sin_propuestas(client, auth_admin_headers, usuario_admin):
    resp = client.post("/api/ia/confirmar-dia", json={"fecha": str(MANANA)},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmadas"] == 0
    assert body["omitidas"] == 0


def test_confirmar_dia_supervisor_solo_su_area(client, auth_supervisor_norte_headers,
                                               db_session, programacion, ruta, chofer_norte,
                                               chofer_sur, usuario_admin, area_norte,
                                               area_sur, usuario_supervisor_norte):
    h1 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(8, 0))
    h2 = _horario(db_session, programacion, ruta, fecha=MANANA, hora=time(14, 0), turno="tarde")
    _asignar(db_session, h1, chofer_norte, area_norte, usuario_admin)
    asig_sur = _asignar(db_session, h2, chofer_sur, area_sur, usuario_admin)

    resp = client.post("/api/ia/confirmar-dia", json={"fecha": str(MANANA)},
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.json()["confirmadas"] == 1

    db_session.expire_all()
    assert db_session.get(Asignacion, asig_sur.id).estado == "propuesta"
