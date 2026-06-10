from datetime import date, datetime, time
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.chofer import Chofer
from app.models.acceso_chofer import AccesoChofer
from app.models.usuario import Usuario
from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio
from app.schemas.chofer import ChoferCrear
from app.services import estacion_service
from app.services.auth_service import hash_password

_ESTADOS_VALIDOS = {"activo", "suspendido", "licencia_medica", "vacaciones", "inactivo"}


def listar_choferes(
    db: Session,
    concesionario_id: Optional[int] = None,
    estado: Optional[str] = None,
) -> List[Chofer]:
    q = db.query(Chofer)
    if concesionario_id:
        q = q.filter(Chofer.concesionario_id == concesionario_id)
    if estado:
        q = q.filter(Chofer.estado == estado)
    return q.all()


def obtener_chofer(db: Session, chofer_id: int) -> Optional[Chofer]:
    return db.query(Chofer).filter(Chofer.id == chofer_id).first()


def dni_existe(db: Session, dni: str) -> bool:
    return db.query(Chofer).filter(Chofer.dni == dni).first() is not None


def _email_acceso(dni: str, email_contacto: Optional[str]) -> str:
    if email_contacto and email_contacto.strip():
        return email_contacto.strip().lower()
    return f"{dni}@metrohub.gob.pe"


def validar_concesionario_supervisor(db: Session, usuario_email: str, concesionario_id: int) -> None:
    registro = db.query(Usuario).filter(Usuario.email == usuario_email).first()
    if registro and registro.concesionario_id != concesionario_id:
        raise PermissionError("Solo puede registrar choferes de su concesionario")


def crear_chofer(
    db: Session,
    datos: ChoferCrear,
    creado_por_id: Optional[int] = None,
) -> Chofer:
    email_login = _email_acceso(datos.dni, datos.email)
    if db.query(AccesoChofer).filter(AccesoChofer.email == email_login).first():
        raise ValueError(f"Ya existe un acceso con el correo {email_login}")

    chofer = Chofer(**datos.model_dump())
    db.add(chofer)
    db.flush()

    db.add(AccesoChofer(
        chofer_id=chofer.id,
        email=email_login,
        password_hash=hash_password(datos.dni),
        creado_por=creado_por_id,
        debe_cambiar_password=True,
    ))
    db.commit()
    db.refresh(chofer)
    return chofer


def serializar_chofer_con_acceso(db: Session, chofer: Chofer) -> dict:
    acceso = db.query(AccesoChofer).filter(AccesoChofer.chofer_id == chofer.id).first()
    return {
        "id":                    chofer.id,
        "dni":                   chofer.dni,
        "nombres":               chofer.nombres,
        "apellidos":             chofer.apellidos,
        "fecha_nacimiento":      str(chofer.fecha_nacimiento),
        "telefono":              chofer.telefono,
        "email":                 chofer.email,
        "concesionario_id":      chofer.concesionario_id,
        "numero_licencia":       chofer.numero_licencia,
        "tipo_licencia":         chofer.tipo_licencia,
        "fec_vence_licencia":    str(chofer.fec_vence_licencia),
        "fec_vence_certif_prot": str(chofer.fec_vence_certif_prot),
        "anios_experiencia":     chofer.anios_experiencia,
        "estado":                chofer.estado,
        "acceso_portal": {
            "email":                 acceso.email if acceso else None,
            "password_inicial":      "DNI del chofer",
            "debe_cambiar_password": acceso.debe_cambiar_password if acceso else False,
        },
    }


def actualizar_estado(db: Session, chofer_id: int, estado: str) -> Optional[Chofer]:
    chofer = obtener_chofer(db, chofer_id)
    if not chofer:
        return None
    chofer.estado = estado
    db.commit()
    db.refresh(chofer)
    return chofer


def alertas_documentos(db: Session, dias_limite: int = 30) -> list:
    hoy = date.today()
    choferes = db.query(Chofer).filter(Chofer.estado == "activo").all()
    alertas = []
    for c in choferes:
        dias_certif   = (c.fec_vence_certif_prot - hoy).days
        dias_licencia = (c.fec_vence_licencia - hoy).days
        if dias_certif <= dias_limite or dias_licencia <= dias_limite:
            alertas.append({
                "id":                    c.id,
                "nombres":               c.nombres,
                "apellidos":             c.apellidos,
                "dni":                   c.dni,
                "fec_vence_certif_prot": c.fec_vence_certif_prot,
                "fec_vence_licencia":    c.fec_vence_licencia,
                "dias_certif":           dias_certif,
                "dias_licencia":         dias_licencia,
                "estado":                "VENCIDA" if min(dias_certif, dias_licencia) < 0 else "POR VENCER",
            })
    return alertas


def _a_minutos(hora: time) -> int:
    return hora.hour * 60 + hora.minute


def listar_mis_asignaciones(
    db: Session,
    chofer_id: int,
    fecha: Optional[str] = None,
) -> dict:
    dia = date.fromisoformat(fecha) if fecha else date.today()
    ahora = datetime.now()
    minutos_ahora = ahora.hour * 60 + ahora.minute if ahora.date() == dia else -1

    asignaciones = (
        db.query(Asignacion)
        .join(HorarioServicio)
        .filter(
            Asignacion.chofer_id == chofer_id,
            HorarioServicio.fecha == dia,
            Asignacion.estado.in_(["confirmada", "propuesta"]),
            HorarioServicio.activo.is_(True),
        )
        .options(
            joinedload(Asignacion.horario).joinedload(HorarioServicio.ruta),
        )
        .order_by(HorarioServicio.hora_salida)
        .all()
    )

    resultado = []
    siguiente_id = None

    for asig in asignaciones:
        horario = asig.horario
        ruta = horario.ruta
        salida_min = _a_minutos(horario.hora_salida)
        es_siguiente = (
            siguiente_id is None
            and (minutos_ahora < 0 or salida_min >= minutos_ahora)
        )
        if es_siguiente:
            siguiente_id = asig.id

        estaciones = estacion_service.estaciones_de_ruta(db, ruta.id)
        resultado.append({
            "asignacion_id": asig.id,
            "estado":        asig.estado,
            "bus_placa":     asig.bus_placa,
            "notas":         asig.notas,
            "es_siguiente":  es_siguiente,
            "horario": {
                "id":               horario.id,
                "fecha":            str(horario.fecha),
                "hora_salida":      str(horario.hora_salida)[:5],
                "turno":            horario.turno,
                "duracion_est_min": horario.duracion_est_min,
            },
            "ruta": {
                "id":     ruta.id,
                "codigo": ruta.codigo,
                "nombre": ruta.nombre,
                "tipo":   ruta.tipo,
            },
            "estaciones": estaciones,
        })

    if siguiente_id is None and resultado:
        siguiente_id = resultado[-1]["asignacion_id"]
        for item in resultado:
            item["es_siguiente"] = item["asignacion_id"] == siguiente_id

    chofer = obtener_chofer(db, chofer_id)
    return {
        "fecha":                  str(dia),
        "chofer_id":              chofer_id,
        "chofer_nombre":          f"{chofer.nombres} {chofer.apellidos}" if chofer else "",
        "total":                  len(resultado),
        "siguiente_asignacion_id": siguiente_id,
        "asignaciones":           resultado,
    }
