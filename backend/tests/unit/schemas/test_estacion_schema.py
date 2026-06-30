"""SCRUM-QA-17: pruebas unitarias de validación del schema de estaciones (RF02)."""
import pytest
from pydantic import ValidationError

from app.schemas.estacion import EstacionCrear, RutaEstacionAsignar


def _payload(**overrides):
    base = {
        "codigo": "EST-001",
        "nombre": "Estación Naranjal",
        "tipo": "terminal",
        "tramo": "norte",
    }
    base.update(overrides)
    return base


def test_estacion_crear_valida_completa():
    est = EstacionCrear(**_payload(orden_troncal=1, latitud=-11.99, longitud=-77.06, activa=False))
    assert est.codigo == "EST-001"
    assert est.tipo == "terminal"
    assert est.tramo == "norte"
    assert est.orden_troncal == 1
    assert est.latitud == pytest.approx(-11.99)
    assert est.longitud == pytest.approx(-77.06)
    assert est.activa is False


def test_estacion_crear_opcionales_por_defecto():
    est = EstacionCrear(**_payload())
    assert est.orden_troncal is None
    assert est.latitud is None
    assert est.longitud is None
    assert est.activa is True


@pytest.mark.parametrize("campo", ["codigo", "nombre", "tipo", "tramo"])
def test_estacion_crear_falta_campo_obligatorio(campo):
    payload = _payload()
    del payload[campo]
    with pytest.raises(ValidationError):
        EstacionCrear(**payload)


def test_estacion_crear_no_valida_tipo_ni_tramo_en_schema():
    # La validación de catálogos vive en el router (estaciones.py), no en el
    # schema: valores inválidos pasan aquí y el endpoint responde 400.
    est = EstacionCrear(**_payload(tipo="parada", tramo="oeste"))
    assert est.tipo == "parada"
    assert est.tramo == "oeste"


def test_ruta_estacion_asignar_valida():
    asig = RutaEstacionAsignar(estacion_id=3, orden=1, tiempo_est_min=5)
    assert asig.estacion_id == 3
    assert asig.orden == 1
    assert asig.tiempo_est_min == 5


def test_ruta_estacion_asignar_tiempo_opcional():
    asig = RutaEstacionAsignar(estacion_id=3, orden=2)
    assert asig.tiempo_est_min is None


@pytest.mark.parametrize("campo", ["estacion_id", "orden"])
def test_ruta_estacion_asignar_falta_obligatorio(campo):
    payload = {"estacion_id": 3, "orden": 1}
    del payload[campo]
    with pytest.raises(ValidationError):
        RutaEstacionAsignar(**payload)
