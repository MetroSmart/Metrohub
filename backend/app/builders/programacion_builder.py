"""
Patrón Builder — RF03 (grilla / programación compleja).

Construye horarios y asignaciones paso a paso, con validación antes de persistir.
"""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio
from app.schemas.horario import AsignacionCrear, HorarioCrear


class ProgramacionBuilderError(Exception):
    """Error de validación o configuración incompleta en el builder."""


class ProgramacionBuilder:
    def __init__(self, db: Session):
        self._db = db
        self._horario: Optional[HorarioCrear] = None
        self._asignacion: Optional[AsignacionCrear] = None
        self._asignado_por: Optional[int] = None
        self._activo: bool = True

    def programacion(self, programacion_id: int) -> "ProgramacionBuilder":
        """Atajo: fija programacion_id para el horario siguiente."""
        self._programacion_id = programacion_id
        return self

    def horario(
        self,
        *,
        programacion_id: Optional[int] = None,
        ruta_id: int,
        fecha: date,
        hora_salida: str,
        turno: str,
        duracion_est_min: int = 60,
    ) -> "ProgramacionBuilder":
        prog_id = programacion_id or getattr(self, "_programacion_id", None)
        if prog_id is None:
            raise ProgramacionBuilderError("programacion_id es obligatorio para el horario")
        self._horario = HorarioCrear(
            programacion_id=prog_id,
            ruta_id=ruta_id,
            fecha=fecha,
            hora_salida=hora_salida,
            turno=turno,
            duracion_est_min=duracion_est_min,
        )
        return self

    def desde_horario(self, datos: HorarioCrear) -> "ProgramacionBuilder":
        self._horario = datos
        return self

    def asignacion(
        self,
        *,
        chofer_id: int,
        area_id: int,
        bus_placa: Optional[str] = None,
        notas: Optional[str] = None,
        asignado_por: int,
    ) -> "ProgramacionBuilder":
        self._asignado_por = asignado_por
        self._asignacion_pendiente = {
            "chofer_id": chofer_id,
            "area_id": area_id,
            "bus_placa": bus_placa,
            "notas": notas,
        }
        return self

    def desde_asignacion(self, datos: AsignacionCrear, asignado_por: int) -> "ProgramacionBuilder":
        self._asignacion = datos
        self._asignado_por = asignado_por
        return self

    def activo(self, valor: bool = True) -> "ProgramacionBuilder":
        self._activo = valor
        return self

    def _validar_asignacion(self, horario: HorarioServicio, datos: AsignacionCrear) -> None:
        from app.services import horario_service
        hora = str(horario.hora_salida)[:5]
        if detectar_solapamiento(
            self._db,
            datos.chofer_id,
            horario.fecha,
            hora,
            horario.duracion_est_min,
        ):
            raise ProgramacionBuilderError(
                f"El chofer {datos.chofer_id} tiene un turno solapado ese día"
            )
        if calcular_horas_dia(
            self._db,
            datos.chofer_id,
            horario.fecha,
            horario.duracion_est_min,
        ) > 8:
            raise ProgramacionBuilderError(
                f"El chofer {datos.chofer_id} excedería las 8h máximas"
            )

    def build_horario(self) -> HorarioServicio:
        if not self._horario:
            raise ProgramacionBuilderError("Configure el horario antes de build_horario()")
        horario = HorarioServicio(**self._horario.model_dump())
        horario.activo = self._activo
        self._db.add(horario)
        self._db.commit()
        self._db.refresh(horario)
        return horario

    def _resolver_asignacion(self, horario_id: Optional[int] = None) -> AsignacionCrear:
        if self._asignacion:
            if horario_id is not None:
                return self._asignacion.model_copy(update={"horario_id": horario_id})
            return self._asignacion
        if hasattr(self, "_asignacion_pendiente") and self._asignado_por:
            hid = horario_id
            if hid is None:
                raise ProgramacionBuilderError("horario_id requerido para la asignación")
            p = self._asignacion_pendiente
            return AsignacionCrear(
                horario_id=hid,
                chofer_id=p["chofer_id"],
                area_id=p["area_id"],
                bus_placa=p.get("bus_placa"),
                notas=p.get("notas"),
            )
        raise ProgramacionBuilderError("Configure la asignación antes de build_asignacion()")

    def build_asignacion(self, horario_id: Optional[int] = None) -> Asignacion:
        from app.services import horario_service
        datos = self._resolver_asignacion(horario_id)

        if not self._asignado_por:
            raise ProgramacionBuilderError("asignado_por es obligatorio")

        horario = (
            self._db.query(HorarioServicio)
            .filter(HorarioServicio.id == datos.horario_id)
            .first()
        )
        if not horario:
            raise ProgramacionBuilderError(f"Horario {datos.horario_id} no encontrado")

        self._validar_asignacion(horario, datos)

        asig = Asignacion(**datos.model_dump(), asignado_por=self._asignado_por)
        self._db.add(asig)
        self._db.commit()
        self._db.refresh(asig)
        return asig

    def build_completo(self) -> dict:
        """Horario + asignación opcional en una sola operación (RF03 grilla)."""
        horario = self.build_horario()
        resultado: dict = {"horario": horario}
        if self._asignacion or hasattr(self, "_asignacion_pendiente"):
            self._asignacion = self._resolver_asignacion(horario.id)
            resultado["asignacion"] = self.build_asignacion()
        return resultado
