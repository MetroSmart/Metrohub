from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload
from dotenv import load_dotenv
import os

from app.models.usuario import Usuario
from app.models.acceso_chofer import AccesoChofer

load_dotenv()

SECRET_KEY   = os.getenv("SECRET_KEY")
ALGORITHM    = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN   = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
LOCKOUT_MIN  = int(os.getenv("LOCKOUT_MINUTES", 15))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def crear_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _registrar_fallo(cuenta) -> None:
    cuenta.intentos_fallidos += 1
    if cuenta.intentos_fallidos >= MAX_ATTEMPTS:
        cuenta.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=LOCKOUT_MIN)
        cuenta.intentos_fallidos = 0


def _registrar_exito(cuenta) -> None:
    cuenta.intentos_fallidos = 0
    cuenta.bloqueado_hasta = None
    cuenta.ultimo_login = datetime.utcnow()


def autenticar_usuario(db: Session, email: str, password: str) -> Optional[Usuario]:
    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.activo == True).first()
    if not usuario:
        return None

    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
        return None

    if not verificar_password(password, usuario.password_hash):
        _registrar_fallo(usuario)
        db.commit()
        return None

    _registrar_exito(usuario)
    db.commit()
    return usuario


def autenticar_chofer(db: Session, email: str, password: str) -> Optional[AccesoChofer]:
    acceso = (
        db.query(AccesoChofer)
        .options(joinedload(AccesoChofer.chofer))
        .filter(AccesoChofer.email == email, AccesoChofer.activo == True)
        .first()
    )
    if not acceso:
        return None

    if acceso.bloqueado_hasta and acceso.bloqueado_hasta > datetime.utcnow():
        return None

    if not verificar_password(password, acceso.password_hash):
        _registrar_fallo(acceso)
        db.commit()
        return None

    _registrar_exito(acceso)
    db.commit()
    return acceso


def autenticar(db: Session, email: str, password: str) -> Optional[dict]:
    usuario = autenticar_usuario(db, email, password)
    if usuario:
        return {
            "rol":                   usuario.rol,
            "email":                 usuario.email,
            "nombre":                f"{usuario.nombre} {usuario.apellidos}",
            "chofer_id":             None,
            "area_id":               usuario.area_id,
            "debe_cambiar_password": False,
        }

    acceso = autenticar_chofer(db, email, password)
    if acceso and acceso.chofer:
        return {
            "rol":                   "chofer",
            "email":                 acceso.email,
            "nombre":                f"{acceso.chofer.nombres} {acceso.chofer.apellidos}",
            "chofer_id":             acceso.chofer_id,
            "debe_cambiar_password": acceso.debe_cambiar_password,
        }

    return None


def cambiar_password_primer_ingreso(
    db: Session,
    email: str,
    password_actual: str,
    password_nueva: str,
) -> AccesoChofer:
    acceso = (
        db.query(AccesoChofer)
        .options(joinedload(AccesoChofer.chofer))
        .filter(AccesoChofer.email == email, AccesoChofer.activo == True)
        .first()
    )
    if not acceso:
        raise ValueError("Acceso de chofer no encontrado")
    if not acceso.debe_cambiar_password:
        raise ValueError("No se requiere cambio de contraseña")
    if not verificar_password(password_actual, acceso.password_hash):
        raise ValueError("Contraseña actual incorrecta")
    if len(password_nueva) < 8:
        raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")
    if acceso.chofer and password_nueva == acceso.chofer.dni:
        raise ValueError("La nueva contraseña no puede ser igual al DNI")

    acceso.password_hash = hash_password(password_nueva)
    acceso.debe_cambiar_password = False
    db.commit()
    db.refresh(acceso)
    return acceso


def decodificar_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    if email is None:
        raise JWTError("sub ausente")
    return {
        "email":     email,
        "rol":       payload.get("rol"),
        "nombre":    payload.get("nombre"),
        "chofer_id": payload.get("chofer_id"),
        "area_id":   payload.get("area_id"),
    }
