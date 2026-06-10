"""Reglas de validación de horarios y asignaciones (RF03/RF04)."""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio


def _a_minutos(t: str) -> int:
    hh, mm = str(t)[:5].split(":")
    return int(hh) * 60 + int(mm)


def detectar_solapamiento(
    db: Session,
    chofer_id: int,
    fecha: date,
    hora_salida: str,
    duracion_min: int,
    excluir_asig_id: Optional[int] = None,
) -> bool:
    inicio_nuevo = _a_minutos(hora_salida)
    fin_nuevo = inicio_nuevo + duracion_min

    asigs = (
        db.query(Asignacion)
        .join(HorarioServicio)
        .filter(HorarioServicio.fecha == fecha, Asignacion.chofer_id == chofer_id)
    )
    if excluir_asig_id:
        asigs = asigs.filter(Asignacion.id != excluir_asig_id)

    for a in asigs.all():
        inicio = _a_minutos(a.horario.hora_salida)
        fin = inicio + a.horario.duracion_est_min
        if inicio_nuevo < fin and fin_nuevo > inicio:
            return True
    return False


def calcular_horas_dia(db: Session, chofer_id: int, fecha: date, duracion_min: int) -> int:
    total = duracion_min
    for a in (
        db.query(Asignacion)
        .join(HorarioServicio)
        .filter(HorarioServicio.fecha == fecha, Asignacion.chofer_id == chofer_id)
        .all()
    ):
        total += a.horario.duracion_est_min
    return total // 60
