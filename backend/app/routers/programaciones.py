from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.models.programacion import Programacion
from app.schemas.programacion import ProgramacionCrear

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede realizar esta acción",
        )


def _id_usuario(db: Session, email: str) -> int:
    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": email}).fetchone()
    return row[0] if row else 1


def _serializar(p: Programacion) -> dict:
    return {
        "id":           p.id,
        "nombre":       p.nombre,
        "fecha_inicio": str(p.fecha_inicio),
        "fecha_fin":    str(p.fecha_fin),
        "estado":       p.estado,
        "creado_por":   p.creado_por,
        "observaciones": p.observaciones,
        "created_at":   str(p.created_at),
    }


@router.get("/")
def listar_programaciones(
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    q = db.query(Programacion)
    if estado:
        q = q.filter(Programacion.estado == estado)
    total = q.count()
    progs = q.order_by(Programacion.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "programaciones": [_serializar(p) for p in progs]}


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_programacion(
    datos: ProgramacionCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    creado_por = _id_usuario(db, usuario["email"])
    prog = Programacion(
        nombre=datos.nombre,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        observaciones=datos.observaciones,
        estado="borrador",
        creado_por=creado_por,
    )
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return _serializar(prog)


@router.delete("/{programacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_programacion(
    programacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    prog = db.query(Programacion).filter(Programacion.id == programacion_id).first()
    if not prog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {programacion_id} no encontrada",
        )
    if prog.estado not in ("borrador", "revision"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar una programación en estado '{prog.estado}'. Solo se permiten borrador y revisión.",
        )
    db.delete(prog)
    db.commit()


@router.get("/{programacion_id}")
def obtener_programacion(
    programacion_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    prog = db.query(Programacion).filter(Programacion.id == programacion_id).first()
    if not prog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {programacion_id} no encontrada",
        )
    return _serializar(prog)
