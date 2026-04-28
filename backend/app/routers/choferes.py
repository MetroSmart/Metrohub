from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.database import get_db
from app.routers.auth import obtener_usuario_actual

router = APIRouter()


# ── Schemas ────────────────────────────────────
class ChoferBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    licencia: str
    tipo_licencia: str          # A1, A2, A3, etc.
    vencimiento_licencia: date
    concesionario: str
    disponibilidad: str         # disponible, descanso, baja_temporal

class ChoferCrear(ChoferBase):
    pass

class ChoferActualizar(BaseModel):
    disponibilidad: str         # solo se puede actualizar el estado


# ── Base de datos temporal ─────────────────────
choferes_db = [
    {
        "id": 1,
        "nombre": "Carlos",
        "apellido": "Mamani",
        "dni": "45678901",
        "licencia": "L-001234",
        "tipo_licencia": "A3",
        "vencimiento_licencia": "2026-08-15",
        "concesionario": "Empresa Lima Norte SAC",
        "disponibilidad": "disponible"
    },
    {
        "id": 2,
        "nombre": "Jorge",
        "apellido": "Quispe",
        "dni": "34567890",
        "licencia": "L-005678",
        "tipo_licencia": "A3",
        "vencimiento_licencia": "2025-12-01",
        "concesionario": "Empresa Lima Norte SAC",
        "disponibilidad": "descanso"
    },
    {
        "id": 3,
        "nombre": "Luis",
        "apellido": "Flores",
        "dni": "56789012",
        "licencia": "L-009012",
        "tipo_licencia": "A2",
        "vencimiento_licencia": "2026-03-20",
        "concesionario": "Empresa Lima Sur SAC",
        "disponibilidad": "disponible"
    },
]


# ── Endpoints ──────────────────────────────────

@router.get("/")
def listar_choferes(
    concesionario: Optional[str] = None,
    disponibilidad: Optional[str] = None,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF04 — Lista choferes con filtros opcionales.
    - Admin ATU ve todos los choferes.
    - Supervisor solo ve los de su concesionario.
    """
    resultado = choferes_db.copy()

    # Supervisor solo ve su concesionario
    if usuario["rol"] == "supervisor":
        resultado = [
            c for c in resultado
            if c["concesionario"] == concesionario
        ]

    # Filtro opcional por disponibilidad
    if disponibilidad:
        resultado = [
            c for c in resultado
            if c["disponibilidad"] == disponibilidad
        ]

    return resultado


@router.get("/{chofer_id}")
def obtener_chofer(
    chofer_id: int,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF04 — Obtiene el detalle de un chofer por ID.
    """
    chofer = next((c for c in choferes_db if c["id"] == chofer_id), None)
    if not chofer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chofer con id {chofer_id} no encontrado"
        )
    return chofer


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_chofer(
    chofer: ChoferCrear,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF04 — Registra un nuevo chofer.
    Solo supervisor o admin_atu pueden registrar.
    """
    if usuario["rol"] not in ["admin_atu", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para registrar choferes"
        )

    # Verificar DNI duplicado
    if any(c["dni"] == chofer.dni for c in choferes_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un chofer con DNI {chofer.dni}"
        )

    nuevo = {
        "id": len(choferes_db) + 1,
        **chofer.model_dump(),
        "vencimiento_licencia": str(chofer.vencimiento_licencia)
    }
    choferes_db.append(nuevo)
    return nuevo


@router.patch("/{chofer_id}/disponibilidad")
def actualizar_disponibilidad(
    chofer_id: int,
    datos: ChoferActualizar,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF04 — Actualiza el estado de disponibilidad de un chofer.
    Estados válidos: disponible, descanso, baja_temporal
    """
    estados_validos = ["disponible", "descanso", "baja_temporal"]
    if datos.disponibilidad not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Válidos: {estados_validos}"
        )

    for c in choferes_db:
        if c["id"] == chofer_id:
            c["disponibilidad"] = datos.disponibilidad
            return {
                "mensaje": f"Disponibilidad actualizada a '{datos.disponibilidad}'",
                "chofer": c
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Chofer con id {chofer_id} no encontrado"
    )


@router.get("/alertas/licencias")
def alertas_vencimiento(usuario = Depends(obtener_usuario_actual)):
    """
    RF04 / RF06 — Lista choferes con licencia próxima a vencer
    (menos de 60 días) o ya vencida.
    """
    from datetime import datetime
    hoy = date.today()
    alertas = []

    for c in choferes_db:
        venc = date.fromisoformat(c["vencimiento_licencia"])
        dias_restantes = (venc - hoy).days

        if dias_restantes <= 60:
            alertas.append({
                **c,
                "dias_restantes": dias_restantes,
                "estado_licencia": "VENCIDA" if dias_restantes < 0 else "POR VENCER"
            })

    return {
        "total_alertas": len(alertas),
        "choferes": alertas
    }