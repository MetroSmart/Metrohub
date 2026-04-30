from datetime import date
from typing import Optional
from pydantic import BaseModel


class ChoferCrear(BaseModel):
    dni:                   str
    nombres:               str
    apellidos:             str
    fecha_nacimiento:      date
    telefono:              Optional[str] = None
    email:                 Optional[str] = None
    concesionario_id:      int
    numero_licencia:       str
    tipo_licencia:         str  # A-IIIA | A-IIIB | A-IIIC
    fec_vence_licencia:    date
    fec_vence_certif_prot: date
    anios_experiencia:     Optional[int] = None


class ChoferRespuesta(ChoferCrear):
    id:     int
    estado: str

    model_config = {"from_attributes": True}


class ChoferActualizar(BaseModel):
    estado: str  # activo | suspendido | licencia_medica | vacaciones | inactivo


class AlertaCertif(BaseModel):
    id:                    int
    nombres:               str
    apellidos:             str
    dni:                   str
    fec_vence_certif_prot: date
    fec_vence_licencia:    date
    dias_certif:           int
    dias_licencia:         int
    estado:                str
