from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.ruta import RutaCrear
from app.schemas.estacion import RutaEstacionAsignar
from app.services import ruta_service, estacion_service

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


@router.get("/")
def listar_rutas(solo_activas: bool = False, db: Session = Depends(get_db),
                 usuario: dict = Depends(obtener_usuario_actual)):
    return ruta_service.listar_rutas(db, solo_activas)


@router.get("/{ruta_id}")
def obtener_ruta(ruta_id: int, db: Session = Depends(get_db),
                 usuario: dict = Depends(obtener_usuario_actual)):
    ruta = ruta_service.obtener_ruta(db, ruta_id)
    if not ruta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ruta {ruta_id} no encontrada")
    return ruta


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_ruta(datos: RutaCrear, db: Session = Depends(get_db),
               usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    return ruta_service.crear_ruta(db, datos)


@router.put("/{ruta_id}")
def actualizar_ruta(ruta_id: int, datos: RutaCrear, db: Session = Depends(get_db),
                    usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    ruta = ruta_service.actualizar_ruta(db, ruta_id, datos)
    if not ruta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ruta {ruta_id} no encontrada")
    return ruta


@router.patch("/{ruta_id}/estado")
def cambiar_estado(ruta_id: int, activa: bool, db: Session = Depends(get_db),
                   usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    ruta = ruta_service.cambiar_estado(db, ruta_id, activa)
    if not ruta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ruta {ruta_id} no encontrada")
    return {"mensaje": f"Ruta {ruta_id} {'activada' if activa else 'desactivada'}", "ruta": ruta}


@router.get("/{ruta_id}/estaciones")
def listar_estaciones_ruta(
    ruta_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    ruta = ruta_service.obtener_ruta(db, ruta_id)
    if not ruta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ruta {ruta_id} no encontrada")
    return estacion_service.estaciones_de_ruta(db, ruta_id)


@router.post("/{ruta_id}/estaciones", status_code=status.HTTP_201_CREATED)
def asignar_estacion(
    ruta_id: int,
    datos: RutaEstacionAsignar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if not ruta_service.obtener_ruta(db, ruta_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ruta {ruta_id} no encontrada")
    if not estacion_service.obtener_estacion(db, datos.estacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Estación {datos.estacion_id} no encontrada")
    return estacion_service.asignar_a_ruta(db, ruta_id, datos)


@router.delete("/{ruta_id}/estaciones/{estacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def desasignar_estacion(
    ruta_id: int,
    estacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    if not estacion_service.desasignar_de_ruta(db, ruta_id, estacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Relación ruta {ruta_id} — estación {estacion_id} no encontrada")