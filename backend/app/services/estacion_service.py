from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.estacion import Estacion
from app.models.ruta import RutaEstacion
from app.schemas.estacion import EstacionCrear, RutaEstacionAsignar


def listar_estaciones(
    db: Session,
    tramo: Optional[str] = None,
    tipo: Optional[str] = None,
) -> List[Estacion]:
    q = db.query(Estacion)
    if tramo:
        q = q.filter(Estacion.tramo == tramo)
    if tipo:
        q = q.filter(Estacion.tipo == tipo)
    return q.order_by(Estacion.orden_troncal, Estacion.nombre).all()


def obtener_estacion(db: Session, id: int) -> Optional[Estacion]:
    return db.query(Estacion).filter(Estacion.id == id).first()


def codigo_existe(db: Session, codigo: str) -> bool:
    return db.query(Estacion).filter(Estacion.codigo == codigo).first() is not None


def crear_estacion(db: Session, datos: EstacionCrear) -> Estacion:
    est = Estacion(**datos.model_dump())
    db.add(est)
    db.commit()
    db.refresh(est)
    return est


def estaciones_de_ruta(db: Session, ruta_id: int) -> List[dict]:
    relaciones = (
        db.query(RutaEstacion)
        .filter(RutaEstacion.ruta_id == ruta_id)
        .options(joinedload(RutaEstacion.estacion))
        .order_by(RutaEstacion.orden)
        .all()
    )
    return [
        {
            "estacion_id":    r.estacion_id,
            "orden":          r.orden,
            "tiempo_est_min": r.tiempo_est_min,
            "codigo":         r.estacion.codigo,
            "nombre":         r.estacion.nombre,
            "tipo":           r.estacion.tipo,
            "tramo":          r.estacion.tramo,
        }
        for r in relaciones
    ]


def asignar_a_ruta(db: Session, ruta_id: int, datos: RutaEstacionAsignar) -> List[dict]:
    existente = db.query(RutaEstacion).filter(
        RutaEstacion.ruta_id == ruta_id,
        RutaEstacion.estacion_id == datos.estacion_id,
    ).first()
    if existente:
        existente.orden = datos.orden
        existente.tiempo_est_min = datos.tiempo_est_min
    else:
        rel = RutaEstacion(
            ruta_id=ruta_id,
            estacion_id=datos.estacion_id,
            orden=datos.orden,
            tiempo_est_min=datos.tiempo_est_min,
        )
        db.add(rel)
    db.commit()
    return estaciones_de_ruta(db, ruta_id)


def desasignar_de_ruta(db: Session, ruta_id: int, estacion_id: int) -> bool:
    rel = db.query(RutaEstacion).filter(
        RutaEstacion.ruta_id == ruta_id,
        RutaEstacion.estacion_id == estacion_id,
    ).first()
    if not rel:
        return False
    db.delete(rel)
    db.commit()
    return True
