from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.builders.programacion_builder import ProgramacionBuilderError
from app.models.programacion import Programacion
from app.schemas.horario import (
    AsignacionCrear,
    DuplicarSemanaRequest,
    HorarioCrear,
    ProgramacionCompletaCrear,
)
from app.services import horario_service
from app.services.duplicar_semana_service import DuplicarSemanaError, duplicar_semana

router = APIRouter()

_ESTADOS_PROG_VALIDOS = {"borrador", "revision", "aprobada", "archivada"}


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el Administrador ATU puede realizar esta acción")


def _usuario_id(db: Session, email: str) -> int:
    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": email}).fetchone()
    return row[0] if row else 1


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


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_horario(datos: HorarioCrear, db: Session = Depends(get_db),
                  usuario: dict = Depends(obtener_usuario_actual)):
    _solo_admin(usuario)
    try:
        return horario_service.crear_horario(db, datos)
    except ProgramacionBuilderError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/duplicar-semana", status_code=status.HTTP_201_CREATED)
def duplicar_semana_grilla(
    datos: DuplicarSemanaRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    asignado_por = _usuario_id(db, usuario["email"])
    try:
        return duplicar_semana(
            db,
            fecha_inicio_origen=datos.fecha_inicio_origen,
            fecha_inicio_destino=datos.fecha_inicio_destino,
            programacion_id=datos.programacion_id,
            programacion_id_destino=datos.programacion_id_destino,
            ruta_id=datos.ruta_id or None,
            incluir_asignaciones=datos.incluir_asignaciones,
            asignado_por=asignado_por,
            omitir_existentes=datos.omitir_existentes,
        )
    except DuplicarSemanaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/programacion-completa", status_code=status.HTTP_201_CREATED)
def crear_programacion_completa(
    datos: ProgramacionCompletaCrear,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    asignado_por = _usuario_id(db, usuario["email"])
    try:
        resultado = horario_service.crear_programacion_completa(
            db, datos, asignado_por if datos.chofer_id else None
        )
        return {
            "horario_id": resultado["horario"].id,
            "asignacion_id": resultado["asignacion"].id if "asignacion" in resultado else None,
        }
    except ProgramacionBuilderError as e:
        sc = status.HTTP_409_CONFLICT if "solapado" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=sc, detail=str(e))


@router.patch("/programacion/{programacion_id}/estado")
def actualizar_estado_programacion(
    programacion_id: int,
    estado: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    if estado not in _ESTADOS_PROG_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Válidos: {sorted(_ESTADOS_PROG_VALIDOS)}",
        )
    if estado == "aprobada":
        _solo_admin(usuario)

    prog = db.query(Programacion).filter(Programacion.id == programacion_id).first()
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Programación {programacion_id} no encontrada")

    prog.estado = estado
    if estado == "aprobada":
        aprobador_id = _usuario_id(db, usuario["email"])
        prog.aprobado_por = aprobador_id
        prog.fecha_aprobacion = datetime.utcnow()

    db.commit()
    return {"programacion_id": programacion_id, "estado": prog.estado}


@router.get("/{horario_id}")
def obtener_horario(horario_id: int, db: Session = Depends(get_db),
                    usuario: dict = Depends(obtener_usuario_actual)):
    horario = horario_service.obtener_horario(db, horario_id)
    if not horario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Horario {horario_id} no encontrado")
    return horario


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
    asignado_por = _usuario_id(db, usuario["email"])
    try:
        return horario_service.crear_asignacion(db, datos, asignado_por)
    except ProgramacionBuilderError as e:
        if "solapado" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
