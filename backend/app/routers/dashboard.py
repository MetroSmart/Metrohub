from fastapi import APIRouter, Depends
from app.routers.auth import obtener_usuario_actual

router = APIRouter()

@router.get("/")
def obtener_kpis(usuario = Depends(obtener_usuario_actual)):
    """
    RF06 — Dashboard de KPIs operativos.
    (En desarrollo)
    """
    return {
        "mensaje": "Dashboard en desarrollo",
        "kpis": {}
    }