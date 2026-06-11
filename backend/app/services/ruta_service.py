from datetime import time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ruta import Ruta
from app.schemas.ruta import RutaCrear


def _normalizar_horas(campos: dict) -> dict:
    # Las columnas hora_inicio/hora_fin son Time; SQLite no acepta strings "HH:MM"
    for campo in ("hora_inicio", "hora_fin"):
        valor = campos.get(campo)
        if isinstance(valor, str):
            campos[campo] = time.fromisoformat(valor)
    return campos


def listar_rutas(db: Session, solo_activas: bool = False) -> List[Ruta]:
    q = db.query(Ruta)
    if solo_activas:
        q = q.filter(Ruta.activa == True)
    return q.all()


def obtener_ruta(db: Session, ruta_id: int) -> Optional[Ruta]:
    return db.query(Ruta).filter(Ruta.id == ruta_id).first()


def crear_ruta(db: Session, datos: RutaCrear) -> Ruta:
    ruta = Ruta(**_normalizar_horas(datos.model_dump()))
    db.add(ruta)
    db.commit()
    db.refresh(ruta)
    return ruta


def actualizar_ruta(db: Session, ruta_id: int, datos: RutaCrear) -> Optional[Ruta]:
    ruta = obtener_ruta(db, ruta_id)
    if not ruta:
        return None
    for campo, valor in _normalizar_horas(datos.model_dump()).items():
        setattr(ruta, campo, valor)
    db.commit()
    db.refresh(ruta)
    return ruta


def cambiar_estado(db: Session, ruta_id: int, activa: bool) -> Optional[Ruta]:
    ruta = obtener_ruta(db, ruta_id)
    if not ruta:
        return None
    ruta.activa = activa
    db.commit()
    db.refresh(ruta)
    return ruta
