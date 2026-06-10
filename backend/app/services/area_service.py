from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.area_operativa import AreaOperativa
from app.schemas.area import AreaCrear


def listar_areas(db: Session, solo_activos: bool = False) -> List[AreaOperativa]:
    q = db.query(AreaOperativa)
    if solo_activos:
        q = q.filter(AreaOperativa.activo == True)  # noqa: E712
    return q.order_by(AreaOperativa.nombre).all()


def obtener_area(db: Session, id: int) -> Optional[AreaOperativa]:
    return db.query(AreaOperativa).filter(AreaOperativa.id == id).first()


def crear_area(db: Session, datos: AreaCrear) -> AreaOperativa:
    area = AreaOperativa(**datos.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def actualizar_area(db: Session, id: int, campos: dict) -> Optional[AreaOperativa]:
    area = obtener_area(db, id)
    if not area:
        return None
    for k, v in campos.items():
        setattr(area, k, v)
    db.commit()
    db.refresh(area)
    return area
