from typing import Optional
from pydantic import BaseModel


class UsuarioCrear(BaseModel):
    email: str
    password: str
    nombre: str
    apellidos: str
    dni: str  # 8 dígitos
    rol: str  # admin_atu | supervisor_area
    area_id: Optional[int] = None


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    activo: Optional[bool] = None


class CambiarPassword(BaseModel):
    nueva_password: str
