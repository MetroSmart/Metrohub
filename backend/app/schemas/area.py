from typing import Optional
from pydantic import BaseModel


class AreaCrear(BaseModel):
    nombre: str
    nombre_corto: str
    descripcion: Optional[str] = None


class AreaActualizar(BaseModel):
    nombre: Optional[str] = None
    nombre_corto: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
