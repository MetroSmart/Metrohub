from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.estacion import EstacionCrear
from app.services import estacion_service

router = APIRouter()

_TIPOS_VALIDOS  = {"terminal", "intermedia", "transferencia"}
_TRAMOS_VALIDOS = {"norte", "centro", "sur"}


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _serializar(e) -> dict:
    return {
        "id":            e.id,
        "codigo":        e.codigo,
        "nombre":        e.nombre,
        "tipo":          e.tipo,
        "tramo":         e.tramo,
        "orden_troncal": e.orden_troncal,
        "latitud":       float(e.latitud)  if e.latitud  else None,
        "longitud":      float(e.longitud) if e.longitud else None,
        "activa":        e.activa,
    }


@router.get("/")
def listar_estaciones(
    tramo: Optional[str] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    ests = estacion_service.listar_estaciones(db, tramo, tipo)
    return {"total": len(ests), "estaciones": [_serializar(e) for e in ests]}


@router.get("/{id}")
def obtener_estacion(
    id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    est = estacion_service.obtener_estacion(db, id)
    if not est:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Estación {id} no encontrada")
    return _serializar(est)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_estacion(
    datos: EstacionCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if datos.tipo not in _TIPOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Tipo inválido. Válidos: {sorted(_TIPOS_VALIDOS)}")
    if datos.tramo not in _TRAMOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Tramo inválido. Válidos: {sorted(_TRAMOS_VALIDOS)}")
    if estacion_service.codigo_existe(db, datos.codigo):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe una estación con código {datos.codigo}")
    return _serializar(estacion_service.crear_estacion(db, datos))
