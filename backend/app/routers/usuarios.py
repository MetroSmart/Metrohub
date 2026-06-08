from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.usuario import UsuarioCrear, UsuarioActualizar, CambiarPassword
from app.services import usuario_service

router = APIRouter()

_ROLES_VALIDOS = {"admin_atu", "supervisor_concesionario"}


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _serializar(u) -> dict:
    return {
        "id":               u.id,
        "email":            u.email,
        "nombre":           u.nombre,
        "apellidos":        u.apellidos,
        "dni":              u.dni,
        "rol":              u.rol,
        "concesionario_id": u.concesionario_id,
        "activo":           u.activo,
        "ultimo_login":     str(u.ultimo_login) if u.ultimo_login else None,
        "created_at":       str(u.created_at),
    }


@router.get("/")
def listar_usuarios(
    rol: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    usuarios = usuario_service.listar_usuarios(db, rol, activo)
    return {"total": len(usuarios), "usuarios": [_serializar(u) for u in usuarios]}


@router.get("/{id}")
def obtener_usuario(
    id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    u = usuario_service.obtener_usuario(db, id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuario {id} no encontrado")
    return _serializar(u)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if datos.rol not in _ROLES_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Rol inválido. Válidos: {sorted(_ROLES_VALIDOS)}")
    if datos.rol == "supervisor_concesionario" and not datos.concesionario_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El supervisor debe tener concesionario_id")
    if datos.rol == "admin_atu" and datos.concesionario_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El admin ATU no puede tener concesionario_id")
    if len(datos.dni) != 8 or not datos.dni.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El DNI debe tener exactamente 8 dígitos numéricos")
    if usuario_service.email_existe(db, datos.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un usuario con email {datos.email}")
    if usuario_service.dni_existe(db, datos.dni):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un usuario con DNI {datos.dni}")
    return _serializar(usuario_service.crear_usuario(db, datos))


@router.patch("/{id}")
def actualizar_usuario(
    id: int,
    datos: UsuarioActualizar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    campos = datos.model_dump(exclude_none=True)
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se enviaron campos para actualizar")
    u = usuario_service.actualizar_usuario(db, id, campos)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuario {id} no encontrado")
    return _serializar(u)


@router.patch("/{id}/password")
def cambiar_password(
    id: int,
    datos: CambiarPassword,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if not datos.nueva_password or len(datos.nueva_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La contraseña debe tener al menos 6 caracteres")
    if not usuario_service.cambiar_password(db, id, datos.nueva_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuario {id} no encontrado")
    return {"mensaje": "Contraseña actualizada"}
