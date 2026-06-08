from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCrear
from app.services.auth_service import pwd_context


def listar_usuarios(
    db: Session,
    rol: Optional[str] = None,
    activo: Optional[bool] = None,
) -> List[Usuario]:
    q = db.query(Usuario)
    if rol:
        q = q.filter(Usuario.rol == rol)
    if activo is not None:
        q = q.filter(Usuario.activo == activo)
    return q.order_by(Usuario.nombre).all()


def obtener_usuario(db: Session, id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == id).first()


def email_existe(db: Session, email: str) -> bool:
    return db.query(Usuario).filter(Usuario.email == email).first() is not None


def dni_existe(db: Session, dni: str) -> bool:
    return db.query(Usuario).filter(Usuario.dni == dni).first() is not None


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    usuario = Usuario(
        email=datos.email,
        password_hash=pwd_context.hash(datos.password),
        nombre=datos.nombre,
        apellidos=datos.apellidos,
        dni=datos.dni,
        rol=datos.rol,
        concesionario_id=datos.concesionario_id,
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_usuario(db: Session, id: int, campos: dict) -> Optional[Usuario]:
    usuario = obtener_usuario(db, id)
    if not usuario:
        return None
    for k, v in campos.items():
        setattr(usuario, k, v)
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_password(db: Session, id: int, nueva_password: str) -> bool:
    usuario = obtener_usuario(db, id)
    if not usuario:
        return False
    usuario.password_hash = pwd_context.hash(nueva_password)
    db.commit()
    return True
