import os
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.services import ia_service


class ChatBody(BaseModel):
    intent: str
    pregunta: str
    params: dict = {}

router = APIRouter()

IA_SERVICE_URL = os.getenv("IA_SERVICE_URL", "http://localhost:8001")

_TTL_ALERTAS = 1800  # 30 minutos
_TTL_CHAT    = 3600  # 1 hora por tipo de conflicto
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


@router.post("/sugerir-reemplazo/{asignacion_id}")
async def sugerir_reemplazo(
    asignacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)

    datos = ia_service.obtener_candidatos_reemplazo(db, asignacion_id)
    if not datos or not datos.get("candidatos"):
        raise HTTPException(status_code=404, detail="No se encontraron candidatos disponibles")

    resultado = await _llamar_ia("/reemplazo", datos)
    return {
        "asignacion_id": asignacion_id,
        "horario": datos["horario"],
        "chofer_ausente": datos["chofer_ausente"],
        "candidatos_evaluados": len(datos["candidatos"]),
        "recomendacion_ia": resultado,
    }


@router.get("/alertas-fatiga")
async def alertas_fatiga(
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin_o_supervisor(usuario)

    cached = _cache_get("alertas_fatiga")
    if cached:
        return {k: v for k, v in cached.items() if k != "_ttl"}

    alertas_raw = ia_service.detectar_alertas_fatiga(db)
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
            "tipo": alerta_raw.get("tipo", ""),
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
