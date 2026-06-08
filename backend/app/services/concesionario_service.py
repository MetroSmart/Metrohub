from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.concesionario import Concesionario
from app.schemas.concesionario import ConcesionarioCrear


def listar_concesionarios(db: Session, solo_activos: bool = False) -> List[Concesionario]:
    q = db.query(Concesionario)
    if solo_activos:
        q = q.filter(Concesionario.activo == True)  # noqa: E712
    return q.order_by(Concesionario.razon_social).all()


def obtener_concesionario(db: Session, id: int) -> Optional[Concesionario]:
    return db.query(Concesionario).filter(Concesionario.id == id).first()


def ruc_existe(db: Session, ruc: str) -> bool:
    return db.query(Concesionario).filter(Concesionario.ruc == ruc).first() is not None


def crear_concesionario(db: Session, datos: ConcesionarioCrear) -> Concesionario:
    conc = Concesionario(**datos.model_dump())
    db.add(conc)
    db.commit()
    db.refresh(conc)
    return conc


def actualizar_concesionario(db: Session, id: int, campos: dict) -> Optional[Concesionario]:
    conc = obtener_concesionario(db, id)
    if not conc:
        return None
    for k, v in campos.items():
        setattr(conc, k, v)
    db.commit()
    db.refresh(conc)
    return conc
