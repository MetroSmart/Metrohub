from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.concesionario import ConcesionarioCrear, ConcesionarioActualizar
from app.services import concesionario_service

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _serializar(c) -> dict:
    return {
        "id":             c.id,
        "ruc":            c.ruc,
        "razon_social":   c.razon_social,
        "nombre_corto":   c.nombre_corto,
        "telefono":       c.telefono,
        "email_contacto": c.email_contacto,
        "activo":         c.activo,
        "created_at":     str(c.created_at),
    }


@router.get("/")
def listar_concesionarios(
    solo_activos: bool = False,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    concs = concesionario_service.listar_concesionarios(db, solo_activos)
    return {"total": len(concs), "concesionarios": [_serializar(c) for c in concs]}


@router.get("/{id}")
def obtener_concesionario(
    id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    conc = concesionario_service.obtener_concesionario(db, id)
    if not conc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Concesionario {id} no encontrado")
    return _serializar(conc)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_concesionario(
    datos: ConcesionarioCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if len(datos.ruc) != 11 or not datos.ruc.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El RUC debe tener exactamente 11 dígitos numéricos")
    if concesionario_service.ruc_existe(db, datos.ruc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un concesionario con RUC {datos.ruc}")
    return _serializar(concesionario_service.crear_concesionario(db, datos))


@router.patch("/{id}")
def actualizar_concesionario(
    id: int,
    datos: ConcesionarioActualizar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    campos = datos.model_dump(exclude_none=True)
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se enviaron campos para actualizar")
    conc = concesionario_service.actualizar_concesionario(db, id, campos)
    if not conc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Concesionario {id} no encontrado")
    return _serializar(conc)
