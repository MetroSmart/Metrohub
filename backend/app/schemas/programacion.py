from datetime import date
from typing import Optional
from pydantic import BaseModel, model_validator


class ProgramacionCrear(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def fin_despues_inicio(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha_inicio")
        return self
