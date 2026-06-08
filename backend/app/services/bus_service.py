from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.bus import Bus
from app.schemas.bus import BusCrear


def listar_buses(
    db: Session,
    concesionario_id: Optional[int] = None,
    estado: Optional[str] = None,
) -> List[Bus]:
    q = db.query(Bus)
    if concesionario_id:
        q = q.filter(Bus.concesionario_id == concesionario_id)
    if estado:
        q = q.filter(Bus.estado == estado)
    return q.order_by(Bus.placa).all()


def obtener_bus(db: Session, placa: str) -> Optional[Bus]:
    return db.query(Bus).filter(Bus.placa == placa).first()


def placa_existe(db: Session, placa: str) -> bool:
    return obtener_bus(db, placa) is not None


def crear_bus(db: Session, datos: BusCrear) -> Bus:
    bus = Bus(**datos.model_dump())
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return bus


def actualizar_bus(db: Session, placa: str, campos: dict) -> Optional[Bus]:
    bus = obtener_bus(db, placa)
    if not bus:
        return None
    for k, v in campos.items():
        setattr(bus, k, v)
    db.commit()
    db.refresh(bus)
    return bus


def eliminar_bus(db: Session, placa: str) -> bool:
    bus = obtener_bus(db, placa)
    if not bus:
        return False
    db.delete(bus)
    db.commit()
    return True
