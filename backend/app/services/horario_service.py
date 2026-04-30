from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto
from app.schemas.horario import HorarioCrear, AsignacionCrear


def _a_minutos(t: str) -> int:
    hh, mm = str(t)[:5].split(":")
    return int(hh) * 60 + int(mm)


# ── Horarios ──────────────────────────────────────────────────

def listar_horarios(db: Session, fecha: Optional[str] = None, ruta_id: Optional[int] = None) -> List[HorarioServicio]:
    q = db.query(HorarioServicio)
    if fecha:
        q = q.filter(HorarioServicio.fecha == fecha)
    if ruta_id:
        q = q.filter(HorarioServicio.ruta_id == ruta_id)
    return q.all()


def obtener_horario(db: Session, horario_id: int) -> Optional[HorarioServicio]:
    return db.query(HorarioServicio).filter(HorarioServicio.id == horario_id).first()


def crear_horario(db: Session, datos: HorarioCrear) -> HorarioServicio:
    horario = HorarioServicio(**datos.model_dump())
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


def eliminar_horario(db: Session, horario_id: int) -> bool:
    horario = obtener_horario(db, horario_id)
    if not horario:
        return False
    db.delete(horario)
    db.commit()
    return True


# ── Asignaciones ──────────────────────────────────────────────

def detectar_solapamiento(
    db: Session, chofer_id: int, fecha: date, hora_salida: str, duracion_min: int,
    excluir_asig_id: Optional[int] = None,
) -> bool:
    inicio_nuevo = _a_minutos(hora_salida)
    fin_nuevo    = inicio_nuevo + duracion_min

    asigs = (
        db.query(Asignacion)
        .join(HorarioServicio)
        .filter(HorarioServicio.fecha == fecha, Asignacion.chofer_id == chofer_id)
    )
    if excluir_asig_id:
        asigs = asigs.filter(Asignacion.id != excluir_asig_id)

    for a in asigs.all():
        inicio = _a_minutos(a.horario.hora_salida)
        fin    = inicio + a.horario.duracion_est_min
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


def crear_asignacion(db: Session, datos: AsignacionCrear, asignado_por: int) -> Asignacion:
    asig = Asignacion(**datos.model_dump(), asignado_por=asignado_por)
    db.add(asig)
    db.commit()
    db.refresh(asig)
    return asig


def listar_conflictos_abiertos(db: Session) -> List[Conflicto]:
    return db.query(Conflicto).filter(Conflicto.resuelto == False).all()
