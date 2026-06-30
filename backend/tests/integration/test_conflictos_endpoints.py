"""Pruebas de integración de /api/conflictos/* (RF03)."""
from datetime import date, time

import pytest

from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto

FECHA = date(2026, 6, 1)


@pytest.fixture
def conflicto(db_session, usuario_admin, area_norte, chofer_norte) -> Conflicto:
    ruta = Ruta(codigo="SIT-1", nombre="Naranjal - Matellini", tipo="regular",
                hora_inicio=time(5, 0), hora_fin=time(23, 0), frecuencia_min=10, activa=True)
    db_session.add(ruta)
    db_session.flush()
    prog = Programacion(nombre="Semana 1", fecha_inicio=FECHA, fecha_fin=date(2026, 6, 7),
                        estado="borrador", creado_por=usuario_admin.id)
    db_session.add(prog)
    db_session.flush()
    horario = HorarioServicio(programacion_id=prog.id, ruta_id=ruta.id, fecha=FECHA,
                              hora_salida=time(8, 0), turno="manana", duracion_est_min=120, activo=True)
    db_session.add(horario)
    db_session.flush()
    asig = Asignacion(horario_id=horario.id, chofer_id=chofer_norte.id, area_id=area_norte.id,
                      estado="propuesta", asignado_por=usuario_admin.id)
    db_session.add(asig)
    db_session.flush()
    c = Conflicto(asignacion_id=asig.id, tipo="solapamiento_turno", severidad="alta",
                  descripcion="Turno solapado", resuelto=False)
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


# ── Listado ───────────────────────────────────────────────
def test_listar_conflictos_ok(client, auth_admin_headers, conflicto):
    resp = client.get("/api/conflictos/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["conflictos"][0]["tipo"] == "solapamiento_turno"


def test_listar_conflictos_filtro_resuelto(client, auth_admin_headers, conflicto):
    resp = client.get("/api/conflictos/?resuelto=false", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    vacio = client.get("/api/conflictos/?resuelto=true", headers=auth_admin_headers)
    assert vacio.json()["total"] == 0


def test_listar_conflictos_sin_token_401(client):
    assert client.get("/api/conflictos/").status_code == 401


# ── Resolución ────────────────────────────────────────────
def test_resolver_conflicto_admin_ok(client, auth_admin_headers, conflicto):
    resp = client.patch(f"/api/conflictos/{conflicto.id}/resolver", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == conflicto.id
    # ahora aparece como resuelto
    resueltos = client.get("/api/conflictos/?resuelto=true", headers=auth_admin_headers)
    assert resueltos.json()["total"] == 1


def test_resolver_conflicto_supervisor_403(client, auth_supervisor_norte_headers, conflicto):
    resp = client.patch(f"/api/conflictos/{conflicto.id}/resolver",
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_resolver_conflicto_404(client, auth_admin_headers):
    resp = client.patch("/api/conflictos/999/resolver", headers=auth_admin_headers)
    assert resp.status_code == 404
