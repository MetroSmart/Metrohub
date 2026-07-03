import datetime as dt
import os
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.asignacion import Asignacion
from app.models.chofer import Chofer
from app.models.conflicto import Conflicto
from app.models.disponibilidad_chofer import DisponibilidadChofer
from app.models.horario_servicio import HorarioServicio
from app.routers.auth import obtener_usuario_actual
from app.services import ia_service


class ChatBody(BaseModel):
    intent: str
    pregunta: str
    params: dict = {}


class DescansoBody(BaseModel):
    fecha: str
    observaciones: str = ""


class ConfirmarDiaBody(BaseModel):
    fecha: str

router = APIRouter()

IA_SERVICE_URL = os.getenv("IA_SERVICE_URL", "http://localhost:8001")

_TTL_ALERTAS    =  300  # 5 minutos
_TTL_CHAT       = 3600  # 1 hora por tipo de conflicto
_TTL_REEMPLAZO  =  600  # 10 minutos por asignación
_cache: dict[str, tuple[float, dict]] = {}


def _cache_get(key: str) -> dict | None:
    entry = _cache.get(key)
    if entry and time.time() - entry[0] < entry[1]["_ttl"]:
        return entry[1]
    return None


def _cache_set(key: str, data: dict, ttl: int) -> None:
    _cache[key] = (time.time(), {**data, "_ttl": ttl})

INTENTS_VALIDOS = {"disponibilidad", "explicar_alerta", "horas_area", "estado_programacion", "resolver_conflicto"}


def _solo_admin_o_supervisor(usuario: dict):
    if usuario["rol"] not in ("admin_atu", "supervisor_area"):
        raise HTTPException(status_code=403, detail="Acceso no autorizado")


def _verificar_area_asignacion(usuario: dict, asig: Asignacion):
    if usuario["rol"] == "supervisor_area" and asig.area_id != usuario.get("area_id"):
        raise HTTPException(
            status_code=403,
            detail="Solo puede operar asignaciones de su área operativa",
        )


def _verificar_area_chofer(usuario: dict, db: Session, chofer_id: int):
    if usuario["rol"] != "supervisor_area":
        return
    row = db.execute(
        text("SELECT area_id FROM choferes WHERE id = :id"), {"id": chofer_id}
    ).fetchone()
    if not row or row[0] != usuario.get("area_id"):
        raise HTTPException(
            status_code=403,
            detail="Solo puede operar choferes de su área operativa",
        )


def _filtrar_alertas_por_area(db: Session, usuario: dict, alertas: list[dict]) -> list[dict]:
    if usuario["rol"] != "supervisor_area":
        return alertas
    area_id = usuario.get("area_id")
    if area_id is None:
        return []
    chofer_ids = {
        c.id
        for c in db.query(Chofer).filter(Chofer.area_id == area_id).all()
    }
    return [a for a in alertas if a.get("chofer_id") in chofer_ids]


def _usuario_id(db: Session, email: str) -> int:
    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": email}).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return row[0]


async def _llamar_ia(path: str, payload: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{IA_SERVICE_URL}{path}", json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"El servicio IA devolvió un error ({e.response.status_code})")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servicio IA no disponible")


@router.get("/health")
async def ia_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{IA_SERVICE_URL}/health")
            return {"ia_service": resp.json()}
    except httpx.RequestError:
        return {"ia_service": "no disponible"}


@router.get("/asignaciones-selector")
async def asignaciones_selector(
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)
    from datetime import date, timedelta
    from app.models.asignacion import Asignacion
    from app.models.horario_servicio import HorarioServicio
    from app.models.conflicto import Conflicto

    hoy = date.today()
    asigs = (
        db.query(Asignacion)
        .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
        .filter(
            Asignacion.estado.in_(["propuesta", "confirmada"]),
            HorarioServicio.fecha >= hoy,
            HorarioServicio.fecha <= hoy + timedelta(days=14),
        )
        .order_by(HorarioServicio.fecha, HorarioServicio.hora_salida)
        .all()
    )

    asigs_validas = [a for a in asigs if a.chofer and a.horario]
    if usuario["rol"] == "supervisor_area":
        area_id = usuario.get("area_id")
        asigs_validas = [a for a in asigs_validas if a.area_id == area_id]
    asig_ids = [a.id for a in asigs_validas]

    conflictos_ids = {
        c.asignacion_id
        for c in db.query(Conflicto.asignacion_id)
        .filter(Conflicto.asignacion_id.in_(asig_ids), Conflicto.resuelto == False)
        .all()
    }

    choferes_con_alerta = {a["chofer_id"] for a in ia_service.detectar_alertas_fatiga(db)}

    TURNO = {"manana": "Mañana", "tarde": "Tarde", "noche": "Noche"}
    resultado = [
        {
            "asignacion_id": a.id,
            "label": (
                f"{a.chofer.nombres} {a.chofer.apellidos}"
                f" — {TURNO.get(a.horario.turno, a.horario.turno)}"
                f" · {a.horario.fecha.strftime('%d %b')}"
                f" · {a.horario.ruta.codigo if a.horario.ruta else 'Ruta ?'}"
            ),
            "tiene_problema": (
                a.id in conflictos_ids or a.chofer_id in choferes_con_alerta
            ),
        }
        for a in asigs_validas
    ]

    resultado.sort(key=lambda x: (0 if x["tiene_problema"] else 1))
    return resultado


@router.post("/sugerir-reemplazo/{asignacion_id}")
async def sugerir_reemplazo(
    asignacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)

    asig = db.query(Asignacion).filter(Asignacion.id == asignacion_id).first()
    if not asig:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    _verificar_area_asignacion(usuario, asig)

    cache_key = f"reemplazo_{asignacion_id}"
    cached = _cache_get(cache_key)
    if cached:
        return {k: v for k, v in cached.items() if k != "_ttl"}

    datos = ia_service.obtener_candidatos_reemplazo(db, asignacion_id)
    if not datos or not datos.get("candidatos"):
        raise HTTPException(status_code=404, detail="No se encontraron candidatos disponibles")

    resultado = await _llamar_ia("/reemplazo", datos)
    response = {
        "asignacion_id": asignacion_id,
        "horario": datos["horario"],
        "chofer_ausente": datos["chofer_ausente"],
        "candidatos_evaluados": len(datos["candidatos"]),
        "recomendacion_ia": resultado,
    }
    _cache_set(cache_key, response, _TTL_REEMPLAZO)
    return response


@router.get("/alertas-fatiga")
async def alertas_fatiga(
    force: bool = False,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)

    if not force:
        cached = _cache_get("alertas_fatiga")
        if cached:
            return {k: v for k, v in cached.items() if k != "_ttl"}

    alertas_raw = ia_service.detectar_alertas_fatiga(db)
    alertas_raw = _filtrar_alertas_por_area(db, usuario, alertas_raw)
    if not alertas_raw:
        result = {"total": 0, "alertas": [], "actualizado_en": int(time.time())}
        _cache_set("alertas_fatiga", result, _TTL_ALERTAS)
        return result

    resultado = await _llamar_ia("/alertas-fatiga", {"alertas": alertas_raw})
    alertas_ia = resultado.get("alertas", [])

    alertas_final = []
    for alerta_ia, alerta_raw in zip(alertas_ia, alertas_raw):
        alertas_final.append({
            **alerta_ia,
            "chofer_id":       alerta_raw.get("chofer_id"),
            "nombres":         alerta_raw.get("nombres", ""),
            "apellidos":       alerta_raw.get("apellidos", ""),
            "tipo":            alerta_raw.get("tipo", ""),
            "fecha_referencia": alerta_raw.get("fecha_referencia", ""),
        })

    result = {
        "total": len(alertas_final),
        "alertas": alertas_final,
        "actualizado_en": int(time.time()),
    }
    _cache_set("alertas_fatiga", result, _TTL_ALERTAS)
    return result


@router.post("/chat")
async def chat_asistente(
    body: ChatBody,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)

    intent   = body.intent
    pregunta = body.pregunta
    params   = body.params

    if intent not in INTENTS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Intent inválido. Válidos: {', '.join(INTENTS_VALIDOS)}"
        )
    if not pregunta:
        raise HTTPException(status_code=400, detail="'pregunta' es requerida")

    cache_key = None
    if intent == "resolver_conflicto":
        cache_key = f"chat_resolver_{params.get('tipo', '')}_{params.get('severidad', '')}"
        cached = _cache_get(cache_key)
        if cached:
            return {k: v for k, v in cached.items() if k != "_ttl"}

    contexto = ia_service.obtener_contexto_chat(db, intent, params)
    resultado = await _llamar_ia("/chat", {
        "intent": intent,
        "contexto": contexto,
        "pregunta": pregunta,
    })
    response = {"intent": intent, "respuesta": resultado.get("respuesta", "")}

    if cache_key:
        _cache_set(cache_key, response, _TTL_CHAT)

    return response


# ─── Acciones IA activas ────────────────────────────────────────────────────

@router.post("/aplicar-reemplazo/{asignacion_id}")
async def aplicar_reemplazo(
    asignacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Busca el mejor reemplazo vía IA y lo aplica: marca la asignación como
    reemplazada, crea la nueva y cierra cualquier conflicto vinculado."""
    _solo_admin_o_supervisor(usuario)

    asig_old = db.query(Asignacion).filter(Asignacion.id == asignacion_id).first()
    if not asig_old:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    _verificar_area_asignacion(usuario, asig_old)

    if asig_old.estado not in ("propuesta", "confirmada"):
        raise HTTPException(
            status_code=400,
            detail="La asignación no está activa para reemplazo",
        )

    cache_key = f"reemplazo_{asignacion_id}"

    # Revalidar candidatos en tiempo real antes de escribir en BD
    datos = ia_service.obtener_candidatos_reemplazo(db, asignacion_id)
    if not datos or not datos.get("candidatos"):
        raise HTTPException(status_code=404, detail="No hay candidatos disponibles para reemplazo")

    candidatos_ids = ia_service.ids_candidatos_validos(datos)
    datos_horario = datos["horario"]
    resultado_ia: dict = {}
    chofer_id_nuevo = None

    cached = _cache_get(cache_key)
    if cached:
        cached_id = cached.get("recomendacion_ia", {}).get("chofer_id_recomendado")
        if cached_id in candidatos_ids:
            chofer_id_nuevo = cached_id
            resultado_ia = cached.get("recomendacion_ia", {})

    if chofer_id_nuevo is None:
        resultado_ia = await _llamar_ia("/reemplazo", datos)
        chofer_id_nuevo = resultado_ia.get("chofer_id_recomendado")

    if chofer_id_nuevo not in candidatos_ids:
        mejor = ia_service.mejor_candidato_deterministico(datos)
        if not mejor:
            raise HTTPException(status_code=404, detail="No hay candidatos disponibles para reemplazo")
        chofer_id_nuevo = mejor["chofer_id"]
        resultado_ia = {
            "chofer_id_recomendado": chofer_id_nuevo,
            "recomendacion": (
                resultado_ia.get("recomendacion")
                or "Reasignado por menor carga horaria (el candidato IA ya no está disponible)."
            ),
        }

    chofer = (
        db.query(Chofer)
        .filter(Chofer.id == chofer_id_nuevo, Chofer.estado == "activo")
        .first()
    )
    if not chofer:
        raise HTTPException(
            status_code=404,
            detail="El chofer recomendado no está disponible",
        )
    if chofer.area_id != asig_old.area_id:
        raise HTTPException(
            status_code=400,
            detail="El chofer recomendado no pertenece al área de la asignación",
        )

    uid = _usuario_id(db, usuario["email"])

    try:
        asig_old.estado = "reemplazada"

        asig_nueva = Asignacion(
            horario_id   = asig_old.horario_id,
            chofer_id    = chofer_id_nuevo,
            bus_placa    = asig_old.bus_placa,
            area_id      = asig_old.area_id,
            estado       = "confirmada",
            asignado_por = uid,
            notas        = f"Reemplazo automático IA — asignación original #{asignacion_id}",
        )
        db.add(asig_nueva)

        for conf in asig_old.conflictos:
            if not conf.resuelto:
                conf.resuelto          = True
                conf.resuelto_por      = uid
                conf.fecha_resolucion  = dt.datetime.utcnow()

        db.commit()
        db.refresh(asig_nueva)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="No se pudo aplicar el reemplazo")

    _cache.pop(cache_key, None)

    return {
        "asignacion_nueva_id": asig_nueva.id,
        "chofer_reemplazo": {
            "id":        chofer.id,
            "nombres":   chofer.nombres,
            "apellidos": chofer.apellidos,
        },
        "recomendacion": resultado_ia.get("recomendacion", ""),
        "horario": datos_horario,
    }


@router.post("/programar-descanso/{chofer_id}")
def programar_descanso(
    chofer_id: int,
    body: DescansoBody,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Registra un día de descanso para el chofer a partir de una alerta de fatiga."""
    _solo_admin_o_supervisor(usuario)
    _verificar_area_chofer(usuario, db, chofer_id)

    fecha = dt.date.fromisoformat(body.fecha)
    uid   = _usuario_id(db, usuario["email"])

    disp = DisponibilidadChofer(
        chofer_id      = chofer_id,
        fecha          = fecha,
        hora_desde     = dt.time(0, 0),
        hora_hasta     = dt.time(23, 59),
        motivo         = "descanso",
        observaciones  = body.observaciones or "Descanso registrado por Copiloto IA — alerta de fatiga detectada",
        registrado_por = uid,
    )
    db.add(disp)

    # Liberar los turnos del chofer en esa fecha para que queden "Sin cubrir"
    asigs_del_dia = (
        db.query(Asignacion)
        .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
        .filter(
            Asignacion.chofer_id == chofer_id,
            HorarioServicio.fecha == fecha,
            Asignacion.estado.in_(["propuesta", "confirmada"]),
        )
        .all()
    )
    if usuario["rol"] == "supervisor_area":
        area_id = usuario.get("area_id")
        if any(a.area_id != area_id for a in asigs_del_dia):
            raise HTTPException(
                status_code=403,
                detail="Solo puede liberar turnos de asignaciones de su área operativa",
            )
    for asig in asigs_del_dia:
        asig.estado = "cancelada"
        asig.notas  = (asig.notas or "") + " | Liberado por descanso compensatorio IA"

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe disponibilidad registrada para esa fecha")

    _cache.pop("alertas_fatiga", None)
    return {
        "mensaje":              "Descanso registrado",
        "fecha":                str(fecha),
        "chofer_id":            chofer_id,
        "turnos_liberados":     len(asigs_del_dia),
    }


@router.post("/confirmar-dia")
def confirmar_dia_ia(
    body: ConfirmarDiaBody,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Confirma todas las asignaciones 'propuesta' del día que no tengan
    conflictos activos. Las que tienen conflictos se omiten."""
    _solo_admin_o_supervisor(usuario)

    fecha = dt.date.fromisoformat(body.fecha)

    propuestas = (
        db.query(Asignacion)
        .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
        .options(joinedload(Asignacion.chofer))
        .filter(HorarioServicio.fecha == fecha, Asignacion.estado == "propuesta")
        .all()
    )
    if usuario["rol"] == "supervisor_area":
        area_id = usuario.get("area_id")
        propuestas = [a for a in propuestas if a.area_id == area_id]

    if not propuestas:
        return {"confirmadas": 0, "omitidas": 0, "detalles_omitidas": [],
                "mensaje": "No hay asignaciones propuestas para esta fecha."}

    propuesta_ids = [a.id for a in propuestas]
    con_conflicto = {
        c.asignacion_id
        for c in db.query(Conflicto)
        .filter(Conflicto.asignacion_id.in_(propuesta_ids), Conflicto.resuelto == False)
        .all()
    }

    confirmadas, omitidas = 0, []
    for asig in propuestas:
        if asig.id not in con_conflicto:
            asig.estado = "confirmada"
            confirmadas += 1
        else:
            omitidas.append({
                "asignacion_id": asig.id,
                "chofer": f"{asig.chofer.nombres} {asig.chofer.apellidos}",
            })

    db.commit()
    total = confirmadas + len(omitidas)
    return {
        "confirmadas":       confirmadas,
        "omitidas":          len(omitidas),
        "detalles_omitidas": omitidas,
        "mensaje": (
            f"IA confirmó {confirmadas} de {total} asignaciones."
            + (f" {len(omitidas)} omitidas por conflictos activos." if omitidas else "")
        ),
    }
