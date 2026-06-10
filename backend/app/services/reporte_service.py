"""Servicio RF06 — exportación con Factory Method y Abstract Factory ATU."""
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.export.factory import ExportadorReporteFactory
from app.factories.reporte_atu_factory import ReporteATUFactory
from app.models.ruta import Ruta
from app.models.bus import Bus
from app.models.chofer import Chofer
from app.models.programacion import Programacion
from app.models.conflicto import Conflicto
from app.services import dashboard_service


def _recopilar_datos(db: Session, extras: dict[str, Any], fecha: date | None = None) -> dict[str, Any]:
    hoy = fecha or date.today()
    en_30_dias = hoy + timedelta(days=30)

    kpis = dashboard_service.obtener_kpis(db)

    rutas = (
        db.query(Ruta).filter(Ruta.activa == True).order_by(Ruta.codigo).all()
    )
    buses = db.query(Bus).order_by(Bus.estado, Bus.placa).all()
    choferes_activos = (
        db.query(Chofer).filter(Chofer.estado == "activo").order_by(Chofer.apellidos).all()
    )
    alertas = (
        db.query(Chofer)
        .filter(
            Chofer.estado == "activo",
            (Chofer.fec_vence_licencia <= en_30_dias)
            | (Chofer.fec_vence_certif_prot <= en_30_dias),
        )
        .order_by(Chofer.fec_vence_licencia)
        .all()
    )
    programaciones = (
        db.query(Programacion)
        .filter(Programacion.estado.in_(["borrador", "revision", "aprobada"]))
        .order_by(Programacion.fecha_inicio.desc())
        .limit(15)
        .all()
    )
    conflictos = (
        db.query(Conflicto)
        .filter(Conflicto.resuelto == False)
        .order_by(Conflicto.id.desc())
        .all()
    )

    return {
        "sistema": "MetroHub",
        "fecha": str(hoy),
        "kpis": {k: v for k, v in kpis.items() if k != "fecha"},
        "rutas": [
            {
                "codigo": r.codigo,
                "nombre": r.nombre,
                "tipo": r.tipo,
                "hora_inicio": str(r.hora_inicio)[:5],
                "hora_fin": str(r.hora_fin)[:5],
                "frecuencia_min": r.frecuencia_min,
            }
            for r in rutas
        ],
        "buses": [
            {
                "placa": b.placa,
                "tipo": b.tipo,
                "anio": b.anio or "—",
                "capacidad": b.capacidad_pasajeros or "—",
                "estado": b.estado,
            }
            for b in buses
        ],
        "choferes": [
            {
                "nombre": f"{c.nombres} {c.apellidos}",
                "licencia": c.tipo_licencia,
                "numero": c.numero_licencia,
                "estado": c.estado,
                "vence_lic": str(c.fec_vence_licencia),
                "vence_certif": str(c.fec_vence_certif_prot),
            }
            for c in choferes_activos
        ],
        "alertas_doc": [
            {
                "nombre": f"{c.nombres} {c.apellidos}",
                "vence_lic": str(c.fec_vence_licencia),
                "dias_lic": (c.fec_vence_licencia - hoy).days,
                "vence_certif": str(c.fec_vence_certif_prot),
                "dias_certif": (c.fec_vence_certif_prot - hoy).days,
            }
            for c in alertas
        ],
        "programaciones": [
            {
                "nombre": p.nombre,
                "estado": p.estado,
                "inicio": str(p.fecha_inicio),
                "fin": str(p.fecha_fin),
            }
            for p in programaciones
        ],
        "conflictos": [
            {
                "tipo": c.tipo.replace("_", " ").capitalize(),
                "descripcion": (c.descripcion or "")[:100],
            }
            for c in conflictos
        ],
        "extras": extras or {},
    }


def exportar_dashboard(
    db: Session,
    formato: str,
    usar_familia_atu: bool = True,
    extras: dict[str, Any] | None = None,
    fecha: date | None = None,
) -> tuple[bytes, str, str]:
    datos = _recopilar_datos(db, extras or {}, fecha)
    if usar_familia_atu:
        return ReporteATUFactory.generar_reporte_completo(formato, datos)
    exportador = ExportadorReporteFactory.crear(formato)
    return exportador.exportar(datos)
