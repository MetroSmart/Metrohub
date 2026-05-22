from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chofer import Chofer
from app.schemas.chofer import ChoferCrear

_ESTADOS_VALIDOS = {"activo", "suspendido", "licencia_medica", "vacaciones", "inactivo"}


def listar_choferes(
    db: Session,
    concesionario_id: Optional[int] = None,
    estado: Optional[str] = None,
) -> List[Chofer]:
    q = db.query(Chofer)
    if concesionario_id:
        q = q.filter(Chofer.concesionario_id == concesionario_id)
    if estado:
        q = q.filter(Chofer.estado == estado)
    return q.all()


def obtener_chofer(db: Session, chofer_id: int) -> Optional[Chofer]:
    return db.query(Chofer).filter(Chofer.id == chofer_id).first()


def dni_existe(db: Session, dni: str) -> bool:
    return db.query(Chofer).filter(Chofer.dni == dni).first() is not None


def crear_chofer(db: Session, datos: ChoferCrear) -> Chofer:
    chofer = Chofer(**datos.model_dump())
    db.add(chofer)
    db.commit()
    db.refresh(chofer)
    return chofer


def actualizar_estado(db: Session, chofer_id: int, estado: str) -> Optional[Chofer]:
    chofer = obtener_chofer(db, chofer_id)
    if not chofer:
        return None
    chofer.estado = estado
    db.commit()
    db.refresh(chofer)
    return chofer


def alertas_documentos(db: Session, dias_limite: int = 30) -> list:
    hoy = date.today()
    choferes = db.query(Chofer).filter(Chofer.estado == "activo").all()
    alertas = []
    for c in choferes:
        dias_certif   = (c.fec_vence_certif_prot - hoy).days
        dias_licencia = (c.fec_vence_licencia - hoy).days
        if dias_certif <= dias_limite or dias_licencia <= dias_limite:
            alertas.append({
                "id":                    c.id,
                "nombres":               c.nombres,
                "apellidos":             c.apellidos,
                "dni":                   c.dni,
                "fec_vence_certif_prot": c.fec_vence_certif_prot,
                "fec_vence_licencia":    c.fec_vence_licencia,
                "dias_certif":           dias_certif,
                "dias_licencia":         dias_licencia,
                "estado":                "VENCIDA" if min(dias_certif, dias_licencia) < 0 else "POR VENCER",
            })
    return alertas
