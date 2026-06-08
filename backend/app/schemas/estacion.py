from typing import Optional
from pydantic import BaseModel


class EstacionCrear(BaseModel):
    codigo: str
    nombre: str
    tipo: str   # terminal | intermedia | transferencia
    tramo: str  # norte | centro | sur
    orden_troncal: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activa: bool = True


class RutaEstacionAsignar(BaseModel):
    estacion_id: int
    orden: int
    tiempo_est_min: Optional[int] = None
