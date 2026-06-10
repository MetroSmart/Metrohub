from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto
from app.builders.programacion_builder import ProgramacionBuilder
from app.schemas.horario import HorarioCrear, AsignacionCrear, ProgramacionCompletaCrear


def _a_minutos(t: str) -> int:
    hh, mm = str(t)[:5].split(":")
    return int(hh) * 60 + int(mm)


# ── Horarios ──────────────────────────────────────────────────

def listar_horarios(db: Session, fecha: Optional[str] = None, ruta_id: Optional[int] = None, programacion_id: Optional[int] = None) -> List[dict]:
    q = (
        db.query(HorarioServicio)
        .options(
            joinedload(HorarioServicio.asignaciones).joinedload(Asignacion.conflictos),
            joinedload(HorarioServicio.asignaciones).joinedload(Asignacion.chofer),
        )
    )
    if fecha:
        q = q.filter(HorarioServicio.fecha == fecha)
    if ruta_id:
        q = q.filter(HorarioServicio.ruta_id == ruta_id)
    if programacion_id:
        q = q.filter(HorarioServicio.programacion_id == programacion_id)

    resultado = []
    for h in q.order_by(HorarioServicio.hora_salida).all():
        conflicto_activo = None
        chofer_info = None
        asignacion_id = None
        for asig in h.asignaciones:
            if chofer_info is None and asig.chofer:
                asignacion_id = asig.id
                chofer_info = {
                    "id":     asig.chofer.id,
                    "nombre": f"{asig.chofer.nombres} {asig.chofer.apellidos}",
                }
            for c in asig.conflictos:
                if not c.resuelto and conflicto_activo is None:
                    conflicto_activo = {
                        "id":            c.id,
                        "asignacion_id": c.asignacion_id,
                        "tipo":          c.tipo,
                        "severidad":     c.severidad,
                        "descripcion":   c.descripcion,
                    }
        bus_placa = next((a.bus_placa for a in h.asignaciones if a.bus_placa), None)
        resultado.append({
            "id":               h.id,
            "programacion_id":  h.programacion_id,
            "ruta_id":          h.ruta_id,
            "fecha":            str(h.fecha),
            "hora_salida":      str(h.hora_salida)[:5],
            "turno":            h.turno,
            "duracion_est_min": h.duracion_est_min,
            "activo":           h.activo,
            "chofer":           chofer_info,
            "asignacion_id":    asignacion_id,
            "bus_placa":        bus_placa,
            "conflicto":        conflicto_activo,
        })
    return resultado


def obtener_horario(db: Session, horario_id: int) -> Optional[HorarioServicio]:
    return db.query(HorarioServicio).filter(HorarioServicio.id == horario_id).first()


def crear_horario(db: Session, datos: HorarioCrear) -> HorarioServicio:
    return ProgramacionBuilder(db).desde_horario(datos).build_horario()


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
    return (
        ProgramacionBuilder(db)
        .desde_asignacion(datos, asignado_por)
        .build_asignacion()
    )


def crear_programacion_completa(
    db: Session, datos: ProgramacionCompletaCrear, asignado_por: int | None
) -> dict:
    horario_data = HorarioCrear(
        programacion_id=datos.programacion_id,
        ruta_id=datos.ruta_id,
        fecha=datos.fecha,
        hora_salida=datos.hora_salida,
        turno=datos.turno,
        duracion_est_min=datos.duracion_est_min,
    )
    builder = ProgramacionBuilder(db).desde_horario(horario_data)
    if datos.chofer_id and datos.area_id and asignado_por:
        builder.asignacion(
            chofer_id=datos.chofer_id,
            area_id=datos.area_id,
            bus_placa=datos.bus_placa,
            notas=datos.notas,
            asignado_por=asignado_por,
        )
    return builder.build_completo()


def listar_conflictos_abiertos(db: Session) -> List[Conflicto]:
    return db.query(Conflicto).filter(Conflicto.resuelto == False).all()
