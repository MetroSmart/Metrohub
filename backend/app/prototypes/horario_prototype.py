"""Prototipo concreto — horario de servicio (RF03 duplicar semana)."""
from datetime import timedelta
from typing import Any

from app.models.horario_servicio import HorarioServicio
from app.prototypes.base import Prototype


class HorarioPrototype(Prototype[HorarioServicio]):
    def __init__(self, estado: dict[str, Any]):
        self._estado = estado

    @classmethod
    def desde_entidad(cls, horario: HorarioServicio) -> "HorarioPrototype":
        return cls({
            "programacion_id": horario.programacion_id,
            "ruta_id": horario.ruta_id,
            "fecha": horario.fecha,
            "hora_salida": horario.hora_salida,
            "turno": horario.turno,
            "duracion_est_min": horario.duracion_est_min,
            "activo": horario.activo,
        })

    def clone(self, **ajustes: Any) -> HorarioServicio:
        data = self._copiar_estado(self._estado)
        if "desplazamiento_dias" in ajustes:
            data["fecha"] = data["fecha"] + timedelta(days=ajustes["desplazamiento_dias"])
        if "programacion_id" in ajustes:
            data["programacion_id"] = ajustes["programacion_id"]
        if "fecha" in ajustes:
            data["fecha"] = ajustes["fecha"]
        return HorarioServicio(**data)
