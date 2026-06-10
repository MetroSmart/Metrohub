from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.chofer import ChoferCrear, ChoferActualizar
from app.services import chofer_service

router = APIRouter()

_ESTADOS_VALIDOS = {"activo", "suspendido", "licencia_medica", "vacaciones", "inactivo"}


def _usuario_id(db: Session, email: str) -> Optional[int]:
    row = db.execute(text("SELECT id FROM usuarios WHERE email = :e"), {"e": email}).fetchone()
    return row[0] if row else None


@router.get("/alertas/documentos")
def alertas_documentos(db: Session = Depends(get_db),
                       usuario: dict = Depends(obtener_usuario_actual)):
    alertas = chofer_service.alertas_documentos(db)
    return {"total_alertas": len(alertas), "choferes": alertas}


@router.get("/me/asignaciones")
def mis_asignaciones(
    fecha: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    if usuario["rol"] != "chofer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los choferes pueden consultar sus asignaciones")
    chofer_id = usuario.get("chofer_id")
    if not chofer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Sesión de chofer inválida")
    return chofer_service.listar_mis_asignaciones(db, chofer_id, fecha)


@router.get("/")
def listar_choferes(
    concesionario_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    return chofer_service.listar_choferes(db, concesionario_id, estado)


@router.get("/{chofer_id}")
def obtener_chofer(chofer_id: int, db: Session = Depends(get_db),
                   usuario: dict = Depends(obtener_usuario_actual)):
    chofer = chofer_service.obtener_chofer(db, chofer_id)
    if not chofer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Chofer {chofer_id} no encontrado")
    return chofer


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_chofer(datos: ChoferCrear, db: Session = Depends(get_db),
                     usuario: dict = Depends(obtener_usuario_actual)):
    if usuario["rol"] not in {"admin_atu", "supervisor_concesionario"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sin permisos para registrar choferes")
    if chofer_service.dni_existe(db, datos.dni):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un chofer con DNI {datos.dni}")
    try:
        if usuario["rol"] == "supervisor_concesionario":
            chofer_service.validar_concesionario_supervisor(
                db, usuario["email"], datos.concesionario_id,
            )
        chofer = chofer_service.crear_chofer(db, datos, creado_por_id=_usuario_id(db, usuario["email"]))
        return chofer_service.serializar_chofer_con_acceso(db, chofer)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{chofer_id}/estado")
def actualizar_estado(chofer_id: int, datos: ChoferActualizar,
                      db: Session = Depends(get_db),
                      usuario: dict = Depends(obtener_usuario_actual)):
    if datos.estado not in _ESTADOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Estado inválido. Válidos: {_ESTADOS_VALIDOS}")
    chofer = chofer_service.actualizar_estado(db, chofer_id, datos.estado)
    if not chofer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Chofer {chofer_id} no encontrado")
    return {"mensaje": f"Estado actualizado a '{datos.estado}'", "chofer": chofer}