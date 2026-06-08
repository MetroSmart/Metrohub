from typing import Optional
from pydantic import BaseModel


class ConcesionarioCrear(BaseModel):
    ruc: str
    razon_social: str
    nombre_corto: str
    telefono: Optional[str] = None
    email_contacto: Optional[str] = None


class ConcesionarioActualizar(BaseModel):
    razon_social: Optional[str] = None
    nombre_corto: Optional[str] = None
    telefono: Optional[str] = None
    email_contacto: Optional[str] = None
    activo: Optional[bool] = None
