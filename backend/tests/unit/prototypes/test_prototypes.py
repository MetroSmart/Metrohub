"""Unit tests para los prototipos de duplicación (RF03 — patrón Prototype)."""
from datetime import date, time

from app.models.horario_servicio import HorarioServicio
from app.models.asignacion import Asignacion
from app.prototypes.horario_prototype import HorarioPrototype
from app.prototypes.asignacion_prototype import AsignacionPrototype


def test_horario_prototype_desplaza_fecha_y_programacion():
    origen = HorarioServicio(
        programacion_id=1, ruta_id=1, fecha=date(2026, 6, 1),
        hora_salida=time(8, 0), turno="manana", duracion_est_min=120, activo=True)
    clon = HorarioPrototype.desde_entidad(origen).clone(
        desplazamiento_dias=7, programacion_id=2)
    assert clon.fecha == date(2026, 6, 8)
    assert clon.programacion_id == 2
    assert clon.hora_salida == time(8, 0)
    assert clon.duracion_est_min == 120
    # el origen no se muta
    assert origen.fecha == date(2026, 6, 1)


def test_horario_prototype_fecha_explicita_tiene_prioridad():
    origen = HorarioServicio(
        programacion_id=1, ruta_id=1, fecha=date(2026, 6, 1),
        hora_salida=time(8, 0), turno="manana", duracion_est_min=120, activo=True)
    clon = HorarioPrototype.desde_entidad(origen).clone(fecha=date(2026, 7, 1))
    assert clon.fecha == date(2026, 7, 1)


def test_asignacion_prototype_clona_como_propuesta():
    origen = Asignacion(
        horario_id=1, chofer_id=5, area_id=1, bus_placa="ABC-123",
        estado="confirmada", asignado_por=10, notas="orig")
    clon = AsignacionPrototype.desde_entidad(origen).clone(horario_id=99, asignado_por=20)
    assert clon.horario_id == 99
    assert clon.asignado_por == 20
    assert clon.chofer_id == 5
    # siempre se clona en estado propuesta, sin conflictos
    assert clon.estado == "propuesta"
