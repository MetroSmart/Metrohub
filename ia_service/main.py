import json
from fastapi import FastAPI, HTTPException
from schemas import (
    ReemplazoRequest, ReemplazoResponse,
    AlertaFatigaRequest, AlertaFatigaResponse, AlertaFatigaTexto,
    ChatRequest, ChatResponse,
)
from prompts import prompt_reemplazo, prompt_alertas_fatiga, prompt_chat
from gemini_client import generar_texto, generar_json

app = FastAPI(title="MetroHub IA Service", version="1.0.0")

_TIPO_FALLBACK = {
    "exceso_horas_semana": (
        "Exceso de horas semanales detectado.",
        "Redistribuir turnos con otros choferes disponibles del área.",
        "alta",
    ),
    "turnos_noche_consecutivos": (
        "Demasiados turnos noche consecutivos.",
        "Programar descanso nocturno y reasignar al menos un turno.",
        "media",
    ),
    "descanso_insuficiente": (
        "Descanso insuficiente entre turnos consecutivos.",
        "Garantizar mínimo 8 horas entre el fin de un turno y el inicio del siguiente.",
        "alta",
    ),
}


def _items_fallback(alertas) -> list[dict]:
    resultado = []
    for a in alertas:
        alerta_txt, sugerencia, sev = _TIPO_FALLBACK.get(
            a.tipo,
            ("Alerta de programación detectada.", "Revisar la asignación del chofer.", "media"),
        )
        resultado.append({"alerta": alerta_txt, "sugerencia": sugerencia, "severidad": sev})
    return resultado


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reemplazo", response_model=ReemplazoResponse)
def sugerir_reemplazo(req: ReemplazoRequest):
    if not req.candidatos:
        raise HTTPException(status_code=400, detail="No hay candidatos disponibles")

    prompt = prompt_reemplazo(
        req.horario.model_dump(),
        [c.model_dump() for c in req.candidatos],
        req.chofer_ausente.model_dump(),
    )
    ids_validos = {c.chofer_id for c in req.candidatos}
    try:
        resultado = generar_json(prompt)
        chofer_id = resultado.get("chofer_id")
        recomendacion = resultado.get("recomendacion", "")
        if chofer_id not in ids_validos:
            raise ValueError("chofer_id retornado no pertenece a los candidatos válidos")
    except (json.JSONDecodeError, ValueError, AttributeError):
        mejor = min(req.candidatos, key=lambda c: (c.horas_semana, c.turnos_noche_consecutivos))
        chofer_id = mejor.chofer_id
        recomendacion = "Recomendado por menor carga horaria y turnos noche consecutivos."
    return ReemplazoResponse(chofer_id_recomendado=chofer_id, recomendacion=recomendacion)


@app.post("/alertas-fatiga", response_model=AlertaFatigaResponse)
def generar_alertas(req: AlertaFatigaRequest):
    if not req.alertas:
        return AlertaFatigaResponse(alertas=[])

    prompt = prompt_alertas_fatiga([a.model_dump() for a in req.alertas])
    try:
        items = generar_json(prompt)
        if not isinstance(items, list):
            raise ValueError("respuesta no es lista")
    except Exception:
        items = _items_fallback(req.alertas)

    resultado = [
        AlertaFatigaTexto(
            chofer_id=alerta_orig.chofer_id,
            nombres=alerta_orig.nombres,
            apellidos=alerta_orig.apellidos,
            alerta=item.get("alerta", ""),
            sugerencia=item.get("sugerencia", ""),
            severidad=item.get("severidad", "media"),
        )
        for item, alerta_orig in zip(items, req.alertas)
    ]
    return AlertaFatigaResponse(alertas=resultado)


@app.post("/chat", response_model=ChatResponse)
def chat_asistente(req: ChatRequest):
    prompt = prompt_chat(req.intent, req.contexto, req.pregunta)
    try:
        respuesta = generar_texto(prompt)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Servicio IA no disponible: {e}")
    return ChatResponse(respuesta=respuesta)
