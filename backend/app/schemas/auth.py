from typing import Optional
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token:           str
    token_type:             str
    rol:                    str
    nombre:                 str = ""
    chofer_id:              Optional[int] = None
    area_id:                Optional[int] = None
    debe_cambiar_password:  bool = False


class PerfilResponse(BaseModel):
    email:                  str
    rol:                    str
    nombre:                 str
    apellidos:              str = ""
    chofer_id:              Optional[int] = None
    area_id:                Optional[int] = None
    debe_cambiar_password:  bool = False


class CambioPasswordPrimerIngreso(BaseModel):
    password_actual: str
    password_nueva:  str
