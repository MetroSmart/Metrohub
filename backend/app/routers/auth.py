from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.schemas.auth import TokenResponse, PerfilResponse
from app.services import auth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return auth_service.decodificar_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = auth_service.autenticar_usuario(db, form.username, form.password)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Correo o contraseña incorrectos")
    token = auth_service.crear_token({
        "sub":    usuario.email,
        "rol":    usuario.rol,
        "nombre": usuario.nombre,
    })
    return TokenResponse(access_token=token, token_type="bearer", rol=usuario.rol)


@router.get("/me", response_model=PerfilResponse)
def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    return PerfilResponse(email=usuario["email"], rol=usuario["rol"], nombre=usuario.get("nombre", ""))
