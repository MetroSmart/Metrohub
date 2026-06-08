from datetime import time as dtime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.disponibilidad_chofer import DisponibilidadChofer
from app.schemas.disponibilidad import DisponibilidadCrear


def _parse_time(s: str) -> dtime:
    h, m = s.strip()[:5].split(":")
    return dtime(int(h), int(m))


def listar(db: Session, chofer_id: Optional[int] = None) -> List[DisponibilidadChofer]:
    q = db.query(DisponibilidadChofer)
    if chofer_id:
        q = q.filter(DisponibilidadChofer.chofer_id == chofer_id)
    return q.order_by(DisponibilidadChofer.fecha.desc(), DisponibilidadChofer.hora_desde).all()


def obtener(db: Session, id: int) -> Optional[DisponibilidadChofer]:
    return db.query(DisponibilidadChofer).filter(DisponibilidadChofer.id == id).first()


def crear(db: Session, datos: DisponibilidadCrear, registrado_por: int) -> DisponibilidadChofer:
    disp = DisponibilidadChofer(
        chofer_id=datos.chofer_id,
        fecha=datos.fecha,
        hora_desde=_parse_time(datos.hora_desde),
        hora_hasta=_parse_time(datos.hora_hasta),
        motivo=datos.motivo,
        observaciones=datos.observaciones,
        registrado_por=registrado_por,
    )
    db.add(disp)
    db.commit()
    db.refresh(disp)
    return disp


def eliminar(db: Session, id: int) -> bool:
    disp = obtener(db, id)
    if not disp:
        return False
    db.delete(disp)
    db.commit()
    return True


def chofer_disponible(db: Session, chofer_id: int, fecha: str, hora: str) -> bool:
    """Devuelve False si el chofer tiene indisponibilidad que cubre fecha/hora."""
    from sqlalchemy import and_
    hora_t = _parse_time(hora)
    conflictos = db.query(DisponibilidadChofer).filter(
        and_(
            DisponibilidadChofer.chofer_id == chofer_id,
            DisponibilidadChofer.fecha == fecha,
            DisponibilidadChofer.hora_desde <= hora_t,
            DisponibilidadChofer.hora_hasta > hora_t,
        )
    ).first()
    return conflictos is None
