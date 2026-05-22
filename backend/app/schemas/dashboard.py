from datetime import date
from pydantic import BaseModel


class DashboardKpis(BaseModel):
    fecha:                  date
    rutas_activas:          int
    choferes_activos:       int
    buses_operativos:       int
    asignaciones_hoy:       int
    conflictos_abiertos:    int
    certif_por_vencer_30d:  int
