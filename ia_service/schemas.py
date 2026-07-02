from pydantic import BaseModel
from typing import Optional


class CandidatoReemplazo(BaseModel):
    chofer_id: int
    nombres: str
    apellidos: str
    horas_semana: float
    turnos_noche_consecutivos: int


class HorarioInfo(BaseModel):
    fecha: str
    hora_salida: str
    turno: str
    ruta_nombre: str


class ChoferAusentInfo(BaseModel):
    nombres: str
    apellidos: str
    motivo: Optional[str] = "no especificado"


class ReemplazoRequest(BaseModel):
    horario: HorarioInfo
    candidatos: list[CandidatoReemplazo]
    chofer_ausente: ChoferAusentInfo


class ReemplazoResponse(BaseModel):
    chofer_id_recomendado: int
    recomendacion: str


class AlertaFatigaItem(BaseModel):
    chofer_id: int
    nombres: str
    apellidos: str
    tipo: str
    detalle: dict


class AlertaFatigaRequest(BaseModel):
    alertas: list[AlertaFatigaItem]


class AlertaFatigaTexto(BaseModel):
    chofer_id: int
    nombres: str
    apellidos: str
    alerta: str
    sugerencia: str
    severidad: str


class AlertaFatigaResponse(BaseModel):
    alertas: list[AlertaFatigaTexto]


class ChatRequest(BaseModel):
    intent: str
    contexto: dict
    pregunta: str


class ChatResponse(BaseModel):
    respuesta: str
