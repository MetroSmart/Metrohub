from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.bus import BusCrear, BusActualizar
from app.services import bus_service

router = APIRouter()

_ESTADOS_VALIDOS = {"operativo", "mantenimiento", "baja", "reparacion"}
_TIPOS_VALIDOS   = {"articulado", "convencional"}


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _admin_o_supervisor_mismo_area(usuario: dict, area_id: int):
    if usuario["rol"] == "admin_atu":
        return
    if usuario["rol"] == "supervisor_area" and usuario.get("area_id") == area_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Solo puede gestionar buses de su área operativa")


def _serializar(b) -> dict:
    return {
        "placa":               b.placa,
        "area_id":             b.area_id,
        "tipo":                b.tipo,
        "anio":                b.anio,
        "capacidad_pasajeros": b.capacidad_pasajeros,
        "estado":              b.estado,
        "created_at":          str(b.created_at),
    }


@router.get("/")
def listar_buses(
    area_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    buses = bus_service.listar_buses(db, area_id, estado)
    return {"total": len(buses), "buses": [_serializar(b) for b in buses]}


@router.get("/{placa}")
def obtener_bus(
    placa: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    bus = bus_service.obtener_bus(db, placa)
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Bus {placa} no encontrado")
    return _serializar(bus)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_bus(
    datos: BusCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _admin_o_supervisor_mismo_area(usuario, datos.area_id)
    if datos.tipo not in _TIPOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Tipo inválido. Válidos: {sorted(_TIPOS_VALIDOS)}")
    if datos.estado not in _ESTADOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Estado inválido. Válidos: {sorted(_ESTADOS_VALIDOS)}")
    if bus_service.placa_existe(db, datos.placa):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un bus con placa {datos.placa}")
    return _serializar(bus_service.crear_bus(db, datos))


@router.patch("/{placa}")
def actualizar_bus(
    placa: str,
    datos: BusActualizar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    bus = bus_service.obtener_bus(db, placa)
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Bus {placa} no encontrado")
    _admin_o_supervisor_mismo_area(usuario, bus.area_id)
    if datos.estado and datos.estado not in _ESTADOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Estado inválido. Válidos: {sorted(_ESTADOS_VALIDOS)}")
    return _serializar(bus_service.actualizar_bus(db, placa, datos.model_dump(exclude_none=True)))


@router.delete("/{placa}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bus(
    placa: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    bus = bus_service.obtener_bus(db, placa)
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Bus {placa} no encontrado")
    _admin_o_supervisor_mismo_area(usuario, bus.area_id)
    bus_service.eliminar_bus(db, placa)
