from typing import Optional
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    rol:          str
    nombre:       str = ""
    chofer_id:    Optional[int] = None


class PerfilResponse(BaseModel):
    email:     str
    rol:       str
    nombre:    str
    apellidos: str = ""
    chofer_id: Optional[int] = None
