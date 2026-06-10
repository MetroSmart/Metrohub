from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.disponibilidad import DisponibilidadCrear
from app.services import disponibilidad_service

router = APIRouter()

_MOTIVOS_VALIDOS = {"descanso", "vacaciones", "medico", "capacitacion", "personal", "otro"}


def _id_usuario(db: Session, email: str) -> int:
    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": email}).fetchone()
    return row[0] if row else 1


def _serializar(d) -> dict:
    return {
        "id":             d.id,
        "chofer_id":      d.chofer_id,
        "fecha":          str(d.fecha),
        "hora_desde":     str(d.hora_desde)[:5],
        "hora_hasta":     str(d.hora_hasta)[:5],
        "motivo":         d.motivo,
        "observaciones":  d.observaciones,
        "registrado_por": d.registrado_por,
        "created_at":     str(d.created_at),
    }


@router.get("/")
def listar_disponibilidad(
    chofer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    disps = disponibilidad_service.listar(db, chofer_id)
    return {"total": len(disps), "disponibilidades": [_serializar(d) for d in disps]}


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_disponibilidad(
    datos: DisponibilidadCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    if usuario["rol"] not in {"admin_atu", "supervisor_area"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sin permisos para registrar disponibilidad")
    if datos.motivo not in _MOTIVOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Motivo inválido. Válidos: {sorted(_MOTIVOS_VALIDOS)}")
    if usuario["rol"] == "supervisor_area":
        row = db.execute(
            text("SELECT area_id FROM choferes WHERE id = :id"), {"id": datos.chofer_id}
        ).fetchone()
        if not row or row[0] != usuario.get("area_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Solo puede registrar disponibilidad de choferes de su área")
    registrado_por = _id_usuario(db, usuario["email"])
    return _serializar(disponibilidad_service.crear(db, datos, registrado_por))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_disponibilidad(
    id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede eliminar registros")
    if not disponibilidad_service.eliminar(db, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Registro {id} no encontrado")
