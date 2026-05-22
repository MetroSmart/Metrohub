from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.services import dashboard_service

router = APIRouter()


@router.get("/")
def obtener_kpis(db: Session = Depends(get_db),
                 usuario: dict = Depends(obtener_usuario_actual)):
    return dashboard_service.obtener_kpis(db)