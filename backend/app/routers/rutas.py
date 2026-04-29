from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.routers.auth import obtener_usuario_actual

router = APIRouter()


# ── Schemas (estructura de datos) ─────────────
class RutaBase(BaseModel):
    codigo: str
    nombre: str
    estacion_inicio: str
    estacion_fin: str
    frecuencia_base: int        # minutos entre buses
    concesionario: str

class RutaCrear(RutaBase):
    pass

class RutaRespuesta(RutaBase):
    id: int
    activa: bool

    class Config:
        from_attributes = True


# ── Base de datos temporal (lista en memoria) ──
# TODO: reemplazar con consulta real a PostgreSQL
# cuando tengamos el modelo Ruta
rutas_db = [
    {
        "id": 1,
        "codigo": "RUTA-A",
        "nombre": "Ruta A — Naranjal a Matellini",
        "estacion_inicio": "Naranjal",
        "estacion_fin": "Matellini",
        "frecuencia_base": 3,
        "concesionario": "Empresa Lima Norte SAC",
        "activa": True
    },
    {
        "id": 2,
        "codigo": "RUTA-B",
        "nombre": "Ruta B — Naranjal a Barranco",
        "estacion_inicio": "Naranjal",
        "estacion_fin": "Barranco",
        "frecuencia_base": 5,
        "concesionario": "Empresa Lima Sur SAC",
        "activa": True
    },
    {
        "id": 3,
        "codigo": "EXPRESO-1",
        "nombre": "Expreso 1 — Naranjal a Plaza Mayor",
        "estacion_inicio": "Naranjal",
        "estacion_fin": "Plaza Mayor",
        "frecuencia_base": 4,
        "concesionario": "Empresa Lima Centro SAC",
        "activa": True
    },
]


# ── Endpoints ──────────────────────────────────

@router.get("/")
def listar_rutas(usuario = Depends(obtener_usuario_actual)):
    """
    RF02 — Lista todas las rutas registradas.
    Requiere autenticación.
    """
    return rutas_db


@router.get("/{ruta_id}")
def obtener_ruta(ruta_id: int, usuario = Depends(obtener_usuario_actual)):
    """
    RF02 — Obtiene el detalle de una ruta por ID.
    """
    ruta = next((r for r in rutas_db if r["id"] == ruta_id), None)
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruta con id {ruta_id} no encontrada"
        )
    return ruta


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_ruta(ruta: RutaCrear, usuario = Depends(obtener_usuario_actual)):
    """
    RF02 — Crea una nueva ruta.
    Solo el Administrador ATU puede crear rutas.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede crear rutas"
        )

    nueva = {
        "id":    len(rutas_db) + 1,
        "activa": True,
        **ruta.model_dump()
    }
    rutas_db.append(nueva)
    return nueva


@router.put("/{ruta_id}")
def actualizar_ruta(
    ruta_id: int,
    ruta: RutaCrear,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF02 — Actualiza los datos de una ruta existente.
    Solo el Administrador ATU puede editar rutas.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede editar rutas"
        )

    for i, r in enumerate(rutas_db):
        if r["id"] == ruta_id:
            rutas_db[i] = {"id": ruta_id, "activa": r["activa"], **ruta.model_dump()}
            return rutas_db[i]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ruta con id {ruta_id} no encontrada"
    )


@router.patch("/{ruta_id}/estado")
def cambiar_estado_ruta(
    ruta_id: int,
    activa: bool,
    usuario = Depends(obtener_usuario_actual)
):
    """
    RF02 — Activa o desactiva una ruta.
    Solo el Administrador ATU puede cambiar el estado.
    """
    if usuario["rol"] != "admin_atu":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el Administrador ATU puede cambiar el estado de rutas"
        )

    for r in rutas_db:
        if r["id"] == ruta_id:
            r["activa"] = activa
            return {
                "mensaje": f"Ruta {ruta_id} {'activada' if activa else 'desactivada'}",
                "ruta": r
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ruta con id {ruta_id} no encontrada"
    )