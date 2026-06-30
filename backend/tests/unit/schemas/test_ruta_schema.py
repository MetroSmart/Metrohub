"""SCRUM-QA-17: pruebas unitarias de validación del schema de rutas (RF02)."""
import pytest
from pydantic import ValidationError

from app.schemas.ruta import RutaCrear, RutaRespuesta


def _payload(**overrides):
    base = {
        "codigo": "SIT-1",
        "nombre": "Naranjal - Matellini",
        "tipo": "regular",
        "hora_inicio": "05:00",
        "hora_fin": "23:00",
        "frecuencia_min": 10,
    }
    base.update(overrides)
    return base


def test_ruta_crear_payload_valido():
    ruta = RutaCrear(**_payload())
    assert ruta.codigo == "SIT-1"
    assert ruta.nombre == "Naranjal - Matellini"
    assert ruta.tipo == "regular"
    assert ruta.hora_inicio == "05:00"
    assert ruta.hora_fin == "23:00"
    assert ruta.frecuencia_min == 10


def test_ruta_crear_frecuencia_limite_inferior():
    assert RutaCrear(**_payload(frecuencia_min=2)).frecuencia_min == 2
    with pytest.raises(ValidationError):
        RutaCrear(**_payload(frecuencia_min=1))


def test_ruta_crear_frecuencia_limite_superior():
    assert RutaCrear(**_payload(frecuencia_min=60)).frecuencia_min == 60
    with pytest.raises(ValidationError):
        RutaCrear(**_payload(frecuencia_min=61))


@pytest.mark.parametrize("campo", ["codigo", "nombre", "tipo", "hora_inicio", "hora_fin", "frecuencia_min"])
def test_ruta_crear_falta_campo_obligatorio(campo):
    payload = _payload()
    del payload[campo]
    with pytest.raises(ValidationError):
        RutaCrear(**payload)


def test_ruta_crear_coerciona_frecuencia_string():
    ruta = RutaCrear(**_payload(frecuencia_min="10"))
    assert ruta.frecuencia_min == 10


def test_ruta_crear_no_valida_formato_hora():
    # Gap conocido: el schema acepta horas malformadas; la validación real
    # queda en manos de la BD/servicio (defecto documentado en QA).
    ruta = RutaCrear(**_payload(hora_inicio="99:99"))
    assert ruta.hora_inicio == "99:99"


def test_ruta_crear_no_valida_tipo():
    # Gap conocido: tipo fuera del catálogo pasa el schema (el CheckConstraint
    # de la tabla es quien lo rechaza).
    ruta = RutaCrear(**_payload(tipo="exprés"))
    assert ruta.tipo == "exprés"


def test_ruta_respuesta_from_attributes():
    class RutaStub:
        id = 1
        codigo = "SIT-1"
        nombre = "Naranjal - Matellini"
        tipo = "regular"
        hora_inicio = "05:00"
        hora_fin = "23:00"
        frecuencia_min = 10
        activa = True

    respuesta = RutaRespuesta.model_validate(RutaStub())
    assert respuesta.id == 1
    assert respuesta.activa is True
    assert respuesta.frecuencia_min == 10
