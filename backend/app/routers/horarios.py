from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.horario import HorarioCrear, AsignacionCrear
from app.services import horario_service

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


@router.get("/conflictos/pendientes")
def listar_conflictos(db: Session = Depends(get_db),
                      usuario: dict = Depends(obtener_usuario_actual)):
    conflictos = horario_service.listar_conflictos_abiertos(db)
    return {"total_conflictos": len(conflictos), "conflictos": conflictos}


@router.get("/")
def listar_horarios(fecha: Optional[str] = None, ruta_id: Optional[int] = None,
                    db: Session = Depends(get_db),
                    usuario: dict = Depends(obtener_usuario_actual)):
    resultado = horario_service.listar_horarios(db, fecha, ruta_id)
    return {"total": len(resultado), "horarios": resultado}


@router.get("/{horario_id}")
def obtener_horario(horario_id: int, db: Session = Depends(get_db),
                    usuario: dict = Depends(obtener_usuario_actual)):
    horario = horario_service.obtener_horario(db, horario_id)
    if not horario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Horario {horario_id} no encontrado")
    return horario


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_horario(datos: HorarioCrear, db: Session = Depends(get_db),
                  usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    return horario_service.crear_horario(db, datos)


@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_horario(horario_id: int, db: Session = Depends(get_db),
                     usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    if not horario_service.eliminar_horario(db, horario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Horario {horario_id} no encontrado")


@router.post("/asignaciones", status_code=status.HTTP_201_CREATED)
def crear_asignacion(datos: AsignacionCrear, db: Session = Depends(get_db),
                     usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)

    horario = horario_service.obtener_horario(db, datos.horario_id)
    if not horario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Horario {datos.horario_id} no encontrado")

    if horario_service.detectar_solapamiento(
        db, datos.chofer_id, horario.fecha,
        str(horario.hora_salida)[:5], horario.duracion_est_min
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El chofer {datos.chofer_id} tiene un turno solapado ese día")

    if horario_service.calcular_horas_dia(
        db, datos.chofer_id, horario.fecha, horario.duracion_est_min
    ) > 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El chofer {datos.chofer_id} excedería las 8h máximas")

    asig_usuario = db.execute(
        __import__("sqlalchemy").text("SELECT id FROM usuarios WHERE email = :e"),
        {"e": usuario["email"]}
    ).fetchone()
    asignado_por = asig_usuario[0] if asig_usuario else 1

    return horario_service.crear_asignacion(db, datos, asignado_por)