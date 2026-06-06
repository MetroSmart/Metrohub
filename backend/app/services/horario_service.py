from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.models.conflicto import Conflicto
from app.builders.programacion_builder import ProgramacionBuilder
from app.schemas.horario import HorarioCrear, AsignacionCrear, ProgramacionCompletaCrear
# ── Horarios ──────────────────────────────────────────────────

def listar_horarios(db: Session, fecha: Optional[str] = None, ruta_id: Optional[int] = None) -> List[dict]:
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

    resultado = []
    for h in q.order_by(HorarioServicio.hora_salida).all():
        conflicto_activo = None
        chofer_info = None
        for asig in h.asignaciones:
            if chofer_info is None and asig.chofer:
                chofer_info = {
                    "id":     asig.chofer.id,
                    "nombre": f"{asig.chofer.nombres} {asig.chofer.apellidos}",
                }
            for c in asig.conflictos:
                if not c.resuelto and conflicto_activo is None:
                    conflicto_activo = {
                        "id":           c.id,
                        "asignacion_id": c.asignacion_id,
                        "tipo":         c.tipo,
                        "severidad":    c.severidad,
                        "descripcion":  c.descripcion,
                    }
        resultado.append({
            "id":              h.id,
            "ruta_id":         h.ruta_id,
            "fecha":           str(h.fecha),
            "hora_salida":     str(h.hora_salida)[:5],
            "turno":           h.turno,
            "duracion_est_min": h.duracion_est_min,
            "activo":          h.activo,
            "chofer":          chofer_info,
            "conflicto":       conflicto_activo,
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
    if datos.chofer_id and datos.concesionario_id and asignado_por:
        builder.asignacion(
            chofer_id=datos.chofer_id,
            concesionario_id=datos.concesionario_id,
            bus_placa=datos.bus_placa,
            notas=datos.notas,
            asignado_por=asignado_por,
        )
    return builder.build_completo()


def listar_conflictos_abiertos(db: Session) -> List[Conflicto]:
    return db.query(Conflicto).filter(Conflicto.resuelto == False).all()
