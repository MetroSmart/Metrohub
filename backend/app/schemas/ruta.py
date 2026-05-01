from datetime import time
from typing import Optional
from pydantic import BaseModel, Field


class RutaCrear(BaseModel):
    codigo:        str
    nombre:        str
    tipo:          str  # regular | expreso | nocturna
    hora_inicio:   str  # "HH:MM"
    hora_fin:      str
    frecuencia_min: int = Field(ge=2, le=60)


class RutaRespuesta(BaseModel):
    id:            int
    codigo:        str
    nombre:        str
    tipo:          str
    hora_inicio:   str
    hora_fin:      str
    frecuencia_min: int
    activa:        bool

    model_config = {"from_attributes": True}
