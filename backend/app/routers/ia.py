import os
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

INTENTS_VALIDOS = {"disponibilidad", "explicar_alerta", "horas_area", "estado_programacion"}


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

    alertas_raw = ia_service.detectar_alertas_fatiga(db)
    if not alertas_raw:
        return {"total": 0, "alertas": [], "mensaje": "No se detectaron alertas esta semana"}

    resultado = await _llamar_ia("/alertas-fatiga", {"alertas": alertas_raw})
    return {
        "total": len(resultado.get("alertas", [])),
        "alertas": resultado.get("alertas", []),
    }


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

    contexto = ia_service.obtener_contexto_chat(db, intent, params)
    resultado = await _llamar_ia("/chat", {
        "intent": intent,
        "contexto": contexto,
        "pregunta": pregunta,
    })
    return {"intent": intent, "respuesta": resultado.get("respuesta", "")}
