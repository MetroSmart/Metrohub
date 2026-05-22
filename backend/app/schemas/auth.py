from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    rol:          str


class PerfilResponse(BaseModel):
    email:    str
    rol:      str
    nombre:   str
