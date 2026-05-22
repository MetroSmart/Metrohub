from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.ruta import Ruta
from app.models.chofer import Chofer
from app.models.bus import Bus
from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio
from app.models.conflicto import Conflicto


def obtener_kpis(db: Session) -> dict:
    hoy = date.today()
    en_30_dias = hoy + timedelta(days=30)

    return {
        "fecha": hoy,
        "rutas_activas":   db.query(Ruta).filter(Ruta.activa == True).count(),
        "choferes_activos": db.query(Chofer).filter(Chofer.estado == "activo").count(),
        "buses_operativos": db.query(Bus).filter(Bus.estado == "operativo").count(),
        "asignaciones_hoy": (
            db.query(Asignacion)
            .join(HorarioServicio)
            .filter(HorarioServicio.fecha == hoy, Asignacion.estado == "confirmada")
            .count()
        ),
        "conflictos_abiertos": db.query(Conflicto).filter(Conflicto.resuelto == False).count(),
        "certif_por_vencer_30d": (
            db.query(Chofer)
            .filter(Chofer.fec_vence_certif_prot <= en_30_dias, Chofer.estado == "activo")
            .count()
        ),
    }
