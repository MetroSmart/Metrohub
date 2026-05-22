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


class DuplicarSemanaRequest(BaseModel):
    """RF03 — Prototype: copiar grilla de una semana a otra."""

    fecha_inicio_origen: date
    fecha_inicio_destino: date
    programacion_id: Optional[int] = None
    programacion_id_destino: Optional[int] = None
    ruta_id: Optional[int] = None
    incluir_asignaciones: bool = True
    omitir_existentes: bool = True


class ProgramacionCompletaCrear(BaseModel):
    """RF03 — horario + asignación opcional (patrón Builder)."""

    programacion_id:  int
    ruta_id:          int
    fecha:            date
    hora_salida:      str
    turno:            str
    duracion_est_min: int = Field(ge=15, le=240)
    chofer_id:        Optional[int] = None
    concesionario_id: Optional[int] = None
    bus_placa:        Optional[str] = None
    notas:            Optional[str] = None
