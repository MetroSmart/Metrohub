"""
Patrón Prototype — duplicar programación semanal en la grilla (RF03).

Copia horarios (y opcionalmente asignaciones) de una semana origen a una destino.
"""
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.builders.programacion_builder import ProgramacionBuilderError
from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio
from app.prototypes.asignacion_prototype import AsignacionPrototype
from app.prototypes.horario_prototype import HorarioPrototype
from app.services.horario_validacion import calcular_horas_dia, detectar_solapamiento


class DuplicarSemanaError(Exception):
    pass


def duplicar_semana(
    db: Session,
    *,
    fecha_inicio_origen: date,
    fecha_inicio_destino: date,
    programacion_id: Optional[int] = None,
    programacion_id_destino: Optional[int] = None,
    ruta_id: Optional[int] = None,
    incluir_asignaciones: bool = True,
    asignado_por: int,
    omitir_existentes: bool = True,
) -> dict:
    if fecha_inicio_destino == fecha_inicio_origen:
        raise DuplicarSemanaError("La semana destino debe ser distinta a la semana origen")

    desplazamiento = (fecha_inicio_destino - fecha_inicio_origen).days
    fin_origen = fecha_inicio_origen + timedelta(days=6)

    q = (
        db.query(HorarioServicio)
        .options(joinedload(HorarioServicio.asignaciones))
        .filter(
            HorarioServicio.fecha >= fecha_inicio_origen,
            HorarioServicio.fecha <= fin_origen,
        )
    )
    if programacion_id:
        q = q.filter(HorarioServicio.programacion_id == programacion_id)
    if ruta_id:
        q = q.filter(HorarioServicio.ruta_id == ruta_id)

    origen = q.order_by(HorarioServicio.fecha, HorarioServicio.hora_salida).all()
    if not origen:
        raise DuplicarSemanaError("No hay horarios en la semana origen para duplicar")

    prog_destino = programacion_id_destino or programacion_id
    horarios_creados: List[HorarioServicio] = []
    asignaciones_creadas: List[Asignacion] = []
    omitidos = 0
    errores: List[str] = []

    for h in origen:
        nuevo = HorarioPrototype.desde_entidad(h).clone(
            desplazamiento_dias=desplazamiento,
            programacion_id=prog_destino,
        )

        if omitir_existentes:
            existe = (
                db.query(HorarioServicio)
                .filter(
                    HorarioServicio.ruta_id == nuevo.ruta_id,
                    HorarioServicio.fecha == nuevo.fecha,
                    HorarioServicio.hora_salida == nuevo.hora_salida,
                )
                .first()
            )
            if existe:
                omitidos += 1
                continue

        db.add(nuevo)
        db.flush()
        horarios_creados.append(nuevo)

        if not incluir_asignaciones:
            continue

        for asig_origen in h.asignaciones:
            if asig_origen.estado == "cancelada":
                continue
            datos_asig = AsignacionPrototype.desde_entidad(asig_origen).clone(
                horario_id=nuevo.id,
                asignado_por=asignado_por,
            )
            try:
                hora = str(nuevo.hora_salida)[:5]
                if detectar_solapamiento(
                    db,
                    datos_asig.chofer_id,
                    nuevo.fecha,
                    hora,
                    nuevo.duracion_est_min,
                ):
                    errores.append(
                        f"Chofer {datos_asig.chofer_id} solapado el {nuevo.fecha} — asignación omitida"
                    )
                    continue
                if calcular_horas_dia(
                    db,
                    datos_asig.chofer_id,
                    nuevo.fecha,
                    nuevo.duracion_est_min,
                ) > 8:
                    errores.append(
                        f"Chofer {datos_asig.chofer_id} excede 8h el {nuevo.fecha} — asignación omitida"
                    )
                    continue
                db.add(datos_asig)
                asignaciones_creadas.append(datos_asig)
            except ProgramacionBuilderError as e:
                errores.append(str(e))

    db.commit()
    for h in horarios_creados:
        db.refresh(h)

    return {
        "desplazamiento_dias": desplazamiento,
        "fecha_inicio_origen": str(fecha_inicio_origen),
        "fecha_inicio_destino": str(fecha_inicio_destino),
        "horarios_duplicados": len(horarios_creados),
        "asignaciones_duplicadas": len(asignaciones_creadas),
        "horarios_omitidos": omitidos,
        "advertencias": errores,
        "horario_ids": [h.id for h in horarios_creados],
    }
