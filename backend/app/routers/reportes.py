from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.schemas.reporte import ExportarReporteRequest
from app.services import reporte_service

router = APIRouter()


def _solo_admin(usuario: dict):
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede exportar reportes",
        )


@router.post("/exportar")
def exportar_reporte(
    body: ExportarReporteRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    _solo_admin(usuario)
    try:
        contenido, media_type, ext = reporte_service.exportar_dashboard(
            db,
            body.formato,
            body.usar_familia_atu,
            body.extras,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    nombre = f"metrohub_reporte_atu.{ext}"
    return Response(
        content=contenido,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
