from datetime import date
from typing import Optional
from pydantic import BaseModel, model_validator


class DisponibilidadCrear(BaseModel):
    chofer_id: int
    fecha: date
    hora_desde: str  # "HH:MM"
    hora_hasta: str  # "HH:MM"
    motivo: str      # descanso | vacaciones | medico | capacitacion | personal | otro
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def horas_validas(self):
        if self.hora_desde >= self.hora_hasta:
            raise ValueError("hora_hasta debe ser mayor que hora_desde")
        return self
