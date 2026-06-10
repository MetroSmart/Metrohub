from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.area import AreaCrear, AreaActualizar
from app.services import area_service

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _serializar(a) -> dict:
    return {
        "id":           a.id,
        "nombre":       a.nombre,
        "nombre_corto": a.nombre_corto,
        "descripcion":  a.descripcion,
        "activo":       a.activo,
        "created_at":   str(a.created_at),
    }


@router.get("/")
def listar_areas(
    solo_activos: bool = False,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    areas = area_service.listar_areas(db, solo_activos)
    return {"total": len(areas), "areas": [_serializar(a) for a in areas]}


@router.get("/{id}")
def obtener_area(
    id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    area = area_service.obtener_area(db, id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Área operativa {id} no encontrada")
    return _serializar(area)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_area(
    datos: AreaCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    return _serializar(area_service.crear_area(db, datos))


@router.patch("/{id}")
def actualizar_area(
    id: int,
    datos: AreaActualizar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    campos = datos.model_dump(exclude_none=True)
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se enviaron campos para actualizar")
    area = area_service.actualizar_area(db, id, campos)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Área operativa {id} no encontrada")
    return _serializar(area)
