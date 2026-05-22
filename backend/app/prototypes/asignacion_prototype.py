"""Prototipo concreto — asignación chofer/turno (sin conflictos)."""
from typing import Any

from app.models.asignacion import Asignacion
from app.prototypes.base import Prototype


class AsignacionPrototype(Prototype[Asignacion]):
    def __init__(self, estado: dict[str, Any]):
        self._estado = estado

    @classmethod
    def desde_entidad(cls, asignacion: Asignacion) -> "AsignacionPrototype":
        return cls({
            "chofer_id": asignacion.chofer_id,
            "bus_placa": asignacion.bus_placa,
            "concesionario_id": asignacion.concesionario_id,
            "estado": "propuesta",
            "asignado_por": asignacion.asignado_por,
            "notas": asignacion.notas,
        })

    def clone(self, **ajustes: Any) -> Asignacion:
        data = self._copiar_estado(self._estado)
        data["estado"] = "propuesta"
        if "horario_id" in ajustes:
            data["horario_id"] = ajustes["horario_id"]
        if "asignado_por" in ajustes:
            data["asignado_por"] = ajustes["asignado_por"]
        return Asignacion(**data)
