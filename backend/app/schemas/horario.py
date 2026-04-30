from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class HorarioCrear(BaseModel):
    programacion_id:  int
    ruta_id:          int
    fecha:            date
    hora_salida:      str   # "HH:MM"
    turno:            str   # manana | tarde | noche
    duracion_est_min: int = Field(ge=15, le=240)


class HorarioRespuesta(BaseModel):
    id:               int
    programacion_id:  int
    ruta_id:          int
    fecha:            date
    hora_salida:      str
    turno:            str
    duracion_est_min: int
    activo:           bool

    model_config = {"from_attributes": True}


class AsignacionCrear(BaseModel):
    horario_id:       int
    chofer_id:        int
    bus_placa:        Optional[str] = None
    concesionario_id: int
    notas:            Optional[str] = None


class AsignacionRespuesta(AsignacionCrear):
    id:     int
    estado: str

    model_config = {"from_attributes": True}
