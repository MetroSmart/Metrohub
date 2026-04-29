from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import date, time

from app.routers.auth import obtener_usuario_actual

router = APIRouter()


# ── Schemas ────────────────────────────────────
class SlotHorario(BaseModel):
    ruta_id: int
    chofer_id: int
    fecha: date
    hora_salida: str            # formato "HH:MM"
    hora_llegada: str           # formato "HH:MM"
    turno: str                  # mañana, tarde, noche

class SlotActualizar(BaseModel):
    chofer_id: Optional[int]    = None
    hora_salida: Optional[str]  = None
    hora_llegada: Optional[str] = None
    turno: Optional[str]        = None


# ── Base de datos temporal ─────────────────────
horarios_db = [
    {
        "id": 1,
        "ruta_id": 1,
        "chofer_id": 1,
        "fecha": "2026-04-28",
        "hora_salida": "06:00",
        "hora_llegada": "14:00",
        "turno": "mañana",
        "conflicto": False
    },
    {
        "id": 2,
        "ruta_id": 2,
        "chofer_id": 3,
        "fecha": "2026-04-28",
        "hora_salida": "14:00",
        "hora_llegada": "22:00",
        "turno": "tarde",
        "conflicto": False
    },
]


# ── Utilidades de validación ───────────────────
def detectar_conflicto(chofer_id: int, fecha: str,
                        hora_salida: str, hora_llegada: str,
                        excluir_id: Optional[int] = None) -> bool:
    """
    Verifica si un chofer ya tiene un turno asignado
    que se solapa con el horario propuesto.
    """
    for h in horarios_db:
        if h["id"] == excluir_id:
            continue
        if h["chofer_id"] != chofer_id or h["fecha"] != fecha:
            continue

        # Convertir a minutos para comparar
        def a_minutos(t: str) -> int:
            hh, mm = t.split(":")
            return int(hh) * 60 + int(mm)

        inicio_nuevo  = a_minutos(hora_salida)
        fin_nuevo     = a_minutos(hora_llegada)
        inicio_existe = a_minutos(h["hora_salida"])
        fin_existe    = a_minutos(h["hora_llegada"])

        # Hay solapamiento si los rangos se superponen
        if inicio_nuevo < fin_existe and fin_nuevo > inicio_existe:
            return True

    return False


def verificar_horas_jornada(chofer_id: int, fecha: str,
                              hora_salida: str, hora_llegada: str) -> int:
    """
    Calcula el total de horas asignadas al chofer en un día.
    Máximo permitido: 8 horas (RF04).
    """
    def a_minutos(t: str) -> int:
        hh, mm = t.split(":")
        return int(hh) * 60 + int(mm)

    total_minutos = a_minutos(hora_llegada) - a_minutos(hora_salida)

    for h in horarios_db:
        if h["chofer_id"] == chofer_id and h["fecha"] == fecha:
            total_minutos += (
                a_minutos(h["hora_llegada"]) - a_minutos(h["hora_salida"])
            )

    return total_minutos // 60  # retorna horas


# ── Endpoints ──────────────────────────────────

@router.get("/")
def listar_horarios(
    fecha: Optional[str]  = None,
    ruta_id: Optional[int] = None,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF03 — Lista todos los slots de horario.
    Filtros opcionales: por fecha o por ruta.
    """
    resultado = horarios_db.copy()

    if fecha:
        resultado = [h for h in resultado if h["fecha"] == fecha]
    if ruta_id:
        resultado = [h for h in resultado if h["ruta_id"] == ruta_id]

    return {
        "total": len(resultado),
        "horarios": resultado
    }


@router.get("/{horario_id}")
def obtener_horario(
    horario_id: int,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF03 — Obtiene el detalle de un slot de horario.
    """
    horario = next((h for h in horarios_db if h["id"] == horario_id), None)
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario con id {horario_id} no encontrado"
        )
    return horario


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_horario(
    slot: SlotHorario,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF03 — Crea un nuevo slot de horario con validación
    de conflictos y horas máximas en tiempo real.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede programar horarios"
        )

    fecha_str       = str(slot.fecha)
    hora_salida     = slot.hora_salida
    hora_llegada    = slot.hora_llegada

    # ── Validación 1: conflicto de turno ─────────
    hay_conflicto = detectar_conflicto(
        slot.chofer_id, fecha_str, hora_salida, hora_llegada
    )
    if hay_conflicto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto: el chofer {slot.chofer_id} ya tiene "
                   f"un turno asignado que se solapa con este horario"
        )

    # ── Validación 2: horas máximas (8h) ─────────
    horas_total = verificar_horas_jornada(
        slot.chofer_id, fecha_str, hora_salida, hora_llegada
    )
    if horas_total > 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El chofer {slot.chofer_id} excedería las 8 horas "
                   f"máximas de conducción ({horas_total}h asignadas)"
        )

    nuevo = {
        "id":           len(horarios_db) + 1,
        "ruta_id":      slot.ruta_id,
        "chofer_id":    slot.chofer_id,
        "fecha":        fecha_str,
        "hora_salida":  hora_salida,
        "hora_llegada": hora_llegada,
        "turno":        slot.turno,
        "conflicto":    False
    }
    horarios_db.append(nuevo)
    return nuevo


@router.put("/{horario_id}")
def actualizar_horario(
    horario_id: int,
    datos: SlotActualizar,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF03 — Actualiza un slot de horario existente
    y re-valida conflictos.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede editar horarios"
        )

    for h in horarios_db:
        if h["id"] == horario_id:
            # Aplicar cambios parciales
            if datos.chofer_id:   h["chofer_id"]   = datos.chofer_id
            if datos.hora_salida: h["hora_salida"]  = datos.hora_salida
            if datos.hora_llegada:h["hora_llegada"] = datos.hora_llegada
            if datos.turno:       h["turno"]        = datos.turno

            # Re-validar conflictos
            hay_conflicto = detectar_conflicto(
                h["chofer_id"], h["fecha"],
                h["hora_salida"], h["hora_llegada"],
                excluir_id=horario_id
            )
            h["conflicto"] = hay_conflicto

            return {
                "mensaje":   "Horario actualizado",
                "conflicto": hay_conflicto,
                "horario":   h
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Horario con id {horario_id} no encontrado"
    )


@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_horario(
    horario_id: int,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF03 — Elimina un slot de horario.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede eliminar horarios"
        )

    for i, h in enumerate(horarios_db):
        if h["id"] == horario_id:
            horarios_db.pop(i)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Horario con id {horario_id} no encontrado"
    )


@router.get("/conflictos/pendientes")
def listar_conflictos(usuario = Depends(obtener_usuario_actual)):
    """
    RF06 — Lista todos los horarios con conflictos
    pendientes de resolución para el dashboard.
    """
    conflictos = [h for h in horarios_db if h["conflicto"]]
    return {
        "total_conflictos": len(conflictos),
        "horarios":         conflictos
    }