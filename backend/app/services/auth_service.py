from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from app.models.usuario import Usuario

load_dotenv()

SECRET_KEY   = os.getenv("SECRET_KEY")
ALGORITHM    = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN   = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
LOCKOUT_MIN  = int(os.getenv("LOCKOUT_MINUTES", 15))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def crear_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(db: Session, email: str, password: str) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.activo == True).first()
    if not usuario:
        return None

    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
        return None

    if not verificar_password(password, usuario.password_hash):
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= MAX_ATTEMPTS:
            usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=LOCKOUT_MIN)
            usuario.intentos_fallidos = 0
        db.commit()
        return None

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_login = datetime.utcnow()
    db.commit()
    return usuario


def decodificar_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    if email is None:
        raise JWTError("sub ausente")
    return {"email": email, "rol": payload.get("rol"), "nombre": payload.get("nombre")}
