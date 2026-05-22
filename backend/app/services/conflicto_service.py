from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conflicto import Conflicto


def listar_conflictos(db: Session, resuelto: Optional[bool] = None) -> List[Conflicto]:
    q = db.query(Conflicto)
    if resuelto is not None:
        q = q.filter(Conflicto.resuelto == resuelto)
    return q.order_by(Conflicto.created_at.desc()).all()


def resolver_conflicto(db: Session, conflicto_id: int, usuario_id: int) -> Optional[Conflicto]:
    conflicto = db.query(Conflicto).filter(Conflicto.id == conflicto_id).first()
    if not conflicto:
        return None
    conflicto.resuelto         = True
    conflicto.resuelto_por     = usuario_id
    conflicto.fecha_resolucion = datetime.utcnow()
    db.commit()
    db.refresh(conflicto)
    return conflicto
