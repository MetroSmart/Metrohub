from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from app.database import get_db

load_dotenv()

router = APIRouter()

# ── Configuración JWT ─────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

# ── Hash de contraseñas ───────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAuth2 ────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Utilidades ────────────────────────────────
def verificar_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def crear_token(data: dict) -> str:
    payload = data.copy()
    expira  = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credencial_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email    = payload.get("sub")
        rol      = payload.get("rol")
        if email is None:
            raise credencial_error
        return {"email": email, "rol": rol}
    except JWTError:
        raise credencial_error


# ── Endpoints ─────────────────────────────────

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    RF01 — Autenticación por correo y contraseña.
    Retorna un token JWT válido por 8 horas.
    """
    # TODO: reemplazar con consulta real a la BD cuando tengamos el modelo Usuario
    # Por ahora usamos un usuario de prueba hardcodeado
    usuarios_prueba = {
        "admin@atu.gob.pe": {
            "password": hashear_password("admin123"),
            "rol": "admin_atu"
        },
        "supervisor@empresa.com": {
            "password": hashear_password("super123"),
            "rol": "supervisor"
        }
    }

    usuario = usuarios_prueba.get(form.username)

    if not usuario or not verificar_password(form.password, usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token({
        "sub": form.username,
        "rol": usuario["rol"]
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "rol":          usuario["rol"]
    }


@router.get("/me")
def obtener_perfil(usuario = Depends(obtener_usuario_actual)):
    """
    Retorna el perfil del usuario autenticado.
    """
    return {
        "email": usuario["email"],
        "rol":   usuario["rol"]
    }