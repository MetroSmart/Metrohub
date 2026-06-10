from typing import Optional
from pydantic import BaseModel


class BusCrear(BaseModel):
    placa: str
    area_id: int
    tipo: str  # articulado | convencional
    anio: Optional[int] = None
    capacidad_pasajeros: Optional[int] = None
    estado: str = "operativo"


class BusActualizar(BaseModel):
    estado: Optional[str] = None
    anio: Optional[int] = None
    capacidad_pasajeros: Optional[int] = None
