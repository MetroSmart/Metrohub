from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.services import conflicto_service

router = APIRouter()


@router.get("/")
def listar_conflictos(
    resuelto: Optional[bool] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    conflictos = conflicto_service.listar_conflictos(db, resuelto)
    return {
        "total": len(conflictos),
        "conflictos": [
            {
                "id":               c.id,
                "asignacion_id":    c.asignacion_id,
                "tipo":             c.tipo,
                "severidad":        c.severidad,
                "descripcion":      c.descripcion,
                "resuelto":         c.resuelto,
                "fecha_resolucion": str(c.fecha_resolucion) if c.fecha_resolucion else None,
                "created_at":       str(c.created_at),
            }
            for c in conflictos
        ],
    }


@router.patch("/{conflicto_id}/resolver")
def resolver_conflicto(
    conflicto_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede resolver conflictos")

    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": usuario["email"]}).fetchone()
    usuario_id = row[0] if row else 1

    conflicto = conflicto_service.resolver_conflicto(db, conflicto_id, usuario_id)
    if not conflicto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Conflicto {conflicto_id} no encontrado")
    return {"mensaje": "Conflicto resuelto", "id": conflicto.id}
