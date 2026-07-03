from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session, joinedload

from app.models.asignacion import Asignacion
from app.models.chofer import Chofer
from app.models.disponibilidad_chofer import DisponibilidadChofer
from app.models.horario_servicio import HorarioServicio
from app.models.programacion import Programacion
from app.models.ruta import Ruta
from app.models.area_operativa import AreaOperativa


# ── Constantes de límites operacionales ──────────────────────────────────────
MAX_HORAS_SEMANA_MIN = 2880      # 48 horas en minutos
MIN_DESCANSO_MIN     = 480       # 8 horas en minutos
MAX_NOCHES_SEGUIDAS  = 3


def _datetime_turno(h: HorarioServicio) -> tuple[datetime, datetime]:
    inicio = datetime.combine(h.fecha, h.hora_salida)
    fin    = inicio + timedelta(minutes=h.duracion_est_min)
    return inicio, fin


def _inicio_semana(d: date) -> date:
    return d - timedelta(days=d.weekday())


# ── 1. Candidatos para reemplazo ─────────────────────────────────────────────

def obtener_candidatos_reemplazo(db: Session, asignacion_id: int) -> dict:
    asignacion = (
        db.query(Asignacion)
        .filter(Asignacion.id == asignacion_id)
        .first()
    )
    if not asignacion:
        return {}

    horario: HorarioServicio = asignacion.horario
    ruta: Ruta = horario.ruta
    inicio_turno, fin_turno = _datetime_turno(horario)
    lunes = _inicio_semana(horario.fecha)
    domingo = lunes + timedelta(days=6)

    choferes_area = (
        db.query(Chofer)
        .filter(Chofer.area_id == asignacion.area_id, Chofer.estado == "activo")
        .all()
    )
    chofer_ids = [c.id for c in choferes_area if c.id != asignacion.chofer_id]

    # Batch query 1: disponibilidades para la fecha del turno
    disp_por_chofer: dict[int, list] = {}
    if chofer_ids:
        for d in (
            db.query(DisponibilidadChofer)
            .filter(
                DisponibilidadChofer.chofer_id.in_(chofer_ids),
                DisponibilidadChofer.fecha == horario.fecha,
            )
            .all()
        ):
            disp_por_chofer.setdefault(d.chofer_id, []).append(d)

    # Batch query 2: asignaciones del día (solapamiento)
    asig_dia_por_chofer: dict[int, list] = {}
    if chofer_ids:
        for a in (
            db.query(Asignacion)
            .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
            .options(joinedload(Asignacion.horario))
            .filter(
                Asignacion.chofer_id.in_(chofer_ids),
                Asignacion.estado.in_(["propuesta", "confirmada"]),
                HorarioServicio.fecha == horario.fecha,
            )
            .all()
        ):
            asig_dia_por_chofer.setdefault(a.chofer_id, []).append(a)

    # Batch query 3: asignaciones de la semana (descanso, horas, noches)
    asig_semana_por_chofer: dict[int, list] = {}
    if chofer_ids:
        for a in (
            db.query(Asignacion)
            .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
            .options(joinedload(Asignacion.horario))
            .filter(
                Asignacion.chofer_id.in_(chofer_ids),
                Asignacion.estado.in_(["propuesta", "confirmada"]),
                HorarioServicio.fecha.between(lunes, domingo),
            )
            .all()
        ):
            asig_semana_por_chofer.setdefault(a.chofer_id, []).append(a)

    candidatos = []
    for chofer in choferes_area:
        if chofer.id == asignacion.chofer_id:
            continue

        bloqueado = disp_por_chofer.get(chofer.id, [])
        if any(
            datetime.combine(d.fecha, d.hora_desde) < fin_turno
            and datetime.combine(d.fecha, d.hora_hasta) > inicio_turno
            for d in bloqueado
        ):
            continue

        otras_asig = asig_dia_por_chofer.get(chofer.id, [])
        solapado = any(
            _datetime_turno(a.horario)[0] < fin_turno
            and _datetime_turno(a.horario)[1] > inicio_turno
            for a in otras_asig
        )
        if solapado:
            continue

        todas_asig_semana = asig_semana_por_chofer.get(chofer.id, [])
        descanso_ok = True
        for a in todas_asig_semana:
            a_inicio, a_fin = _datetime_turno(a.horario)
            if fin_turno <= a_inicio:
                if (a_inicio - fin_turno).total_seconds() < MIN_DESCANSO_MIN * 60:
                    descanso_ok = False
                    break
            elif a_fin <= inicio_turno:
                if (inicio_turno - a_fin).total_seconds() < MIN_DESCANSO_MIN * 60:
                    descanso_ok = False
                    break
            else:
                descanso_ok = False  # solapamiento
                break
        if not descanso_ok:
            continue

        horas_semana = sum(a.horario.duracion_est_min for a in todas_asig_semana) / 60.0
        noches = [
            a for a in sorted(todas_asig_semana, key=lambda x: x.horario.fecha)
            if a.horario.turno == "noche"
        ]
        consecutivos = _max_consecutivos_noche(noches)

        candidatos.append({
            "chofer_id": chofer.id,
            "nombres": chofer.nombres,
            "apellidos": chofer.apellidos,
            "horas_semana": round(horas_semana, 1),
            "turnos_noche_consecutivos": consecutivos,
        })

    candidatos.sort(key=lambda c: (c["horas_semana"], c["turnos_noche_consecutivos"]))

    chofer_ausente = asignacion.chofer
    if not chofer_ausente:
        return {}
    return {
        "horario": {
            "fecha": str(horario.fecha),
            "hora_salida": str(horario.hora_salida),
            "turno": horario.turno,
            "ruta_nombre": ruta.nombre if ruta else "Desconocida",
        },
        "chofer_ausente": {
            "nombres": chofer_ausente.nombres,
            "apellidos": chofer_ausente.apellidos,
            "motivo": "baja/cancelación",
        },
        "candidatos": candidatos[:5],  # top 5
    }


# ── 2. Detección de alertas de fatiga ────────────────────────────────────────

def _max_consecutivos_noche(asignaciones_noche: list) -> int:
    if not asignaciones_noche:
        return 0
    max_consec = consec = 1
    for i in range(1, len(asignaciones_noche)):
        diff = (asignaciones_noche[i].horario.fecha - asignaciones_noche[i-1].horario.fecha).days
        if diff == 1:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 1
    return max_consec


def detectar_alertas_fatiga(db: Session) -> list[dict]:
    hoy   = date.today()
    lunes = _inicio_semana(hoy)
    dom   = lunes + timedelta(days=6)

    asignaciones = (
        db.query(Asignacion)
        .join(HorarioServicio, Asignacion.horario_id == HorarioServicio.id)
        .filter(
            Asignacion.estado.in_(["propuesta", "confirmada"]),
            HorarioServicio.fecha.between(lunes - timedelta(days=7), dom),
        )
        .all()
    )

    por_chofer: dict[int, list[Asignacion]] = {}
    for a in asignaciones:
        por_chofer.setdefault(a.chofer_id, []).append(a)

    alertas = []
    for chofer_id, asigs in por_chofer.items():
        chofer = asigs[0].chofer
        asigs_semana = [
            a for a in asigs
            if lunes <= a.horario.fecha <= dom
        ]
        asigs_ordenadas = sorted(asigs, key=lambda a: (a.horario.fecha, a.horario.hora_salida))

        # alerta: exceso de horas semanales
        min_semana = sum(a.horario.duracion_est_min for a in asigs_semana)
        if min_semana > MAX_HORAS_SEMANA_MIN:
            alertas.append({
                "chofer_id": chofer_id,
                "nombres": chofer.nombres,
                "apellidos": chofer.apellidos,
                "tipo": "exceso_horas_semana",
                "fecha_referencia": str(lunes),
                "detalle": {
                    "horas_asignadas": round(min_semana / 60, 1),
                    "limite_horas": MAX_HORAS_SEMANA_MIN // 60,
                    "semana": str(lunes),
                },
            })

        # alerta: turnos noche consecutivos
        noches = sorted(
            [a for a in asigs_semana if a.horario.turno == "noche"],
            key=lambda a: a.horario.fecha,
        )
        consec = _max_consecutivos_noche(noches)
        if consec > MAX_NOCHES_SEGUIDAS:
            alertas.append({
                "chofer_id": chofer_id,
                "nombres": chofer.nombres,
                "apellidos": chofer.apellidos,
                "tipo": "turnos_noche_consecutivos",
                "fecha_referencia": str(noches[0].horario.fecha) if noches else str(lunes),
                "detalle": {
                    "turnos_consecutivos": consec,
                    "limite": MAX_NOCHES_SEGUIDAS,
                },
            })

        # alerta: descanso insuficiente entre turnos
        for i in range(1, len(asigs_ordenadas)):
            _, fin_ant = _datetime_turno(asigs_ordenadas[i-1].horario)
            ini_sig, _ = _datetime_turno(asigs_ordenadas[i].horario)
            gap_min = (ini_sig - fin_ant).total_seconds() / 60
            if 0 < gap_min < MIN_DESCANSO_MIN:
                alertas.append({
                    "chofer_id": chofer_id,
                    "nombres": chofer.nombres,
                    "apellidos": chofer.apellidos,
                    "tipo": "descanso_insuficiente",
                    "fecha_referencia": str(asigs_ordenadas[i-1].horario.fecha),
                    "detalle": {
                        "descanso_horas": round(gap_min / 60, 1),
                        "minimo_horas": MIN_DESCANSO_MIN // 60,
                        "entre_turnos": (
                            str(asigs_ordenadas[i-1].horario.fecha) +
                            " y " +
                            str(asigs_ordenadas[i].horario.fecha)
                        ),
                    },
                })
                break  # una alerta por chofer en esta categoría

    # Excluir alertas de choferes que ya tienen descanso registrado
    # cerca de la fecha de la alerta (±1 día), porque la acción ya fue tomada.
    if alertas:
        choferes_con_alerta = {a["chofer_id"] for a in alertas}
        fechas_por_chofer: dict[int, list] = {}
        for a in alertas:
            fechas_por_chofer.setdefault(a["chofer_id"], []).append(
                date.fromisoformat(a["fecha_referencia"])
            )

        choferes_descansando = set()
        for chofer_id, fechas_ref in fechas_por_chofer.items():
            for fecha_ref in fechas_ref:
                existe = (
                    db.query(DisponibilidadChofer)
                    .filter(
                        DisponibilidadChofer.chofer_id == chofer_id,
                        DisponibilidadChofer.motivo  == "descanso",
                        DisponibilidadChofer.fecha.between(
                            fecha_ref - timedelta(days=1),
                            fecha_ref + timedelta(days=1),
                        ),
                    )
                    .first()
                )
                if existe:
                    choferes_descansando.add(chofer_id)
                    break

        alertas = [a for a in alertas if a["chofer_id"] not in choferes_descansando]

    return alertas


# ── 3. Contexto para el chat asistente ───────────────────────────────────────

def obtener_contexto_chat(db: Session, intent: str, params: dict) -> dict:
    if intent == "disponibilidad":
        return _ctx_disponibilidad(db, params)
    if intent == "explicar_alerta":
        return _ctx_explicar_alerta(db, params)
    if intent == "horas_area":
        return _ctx_horas_area(db, params)
    if intent == "estado_programacion":
        return _ctx_estado_programacion(db, params)
    if intent == "resolver_conflicto":
        return _ctx_resolver_conflicto(params)
    return {"info": "intent no reconocido"}


def _ctx_resolver_conflicto(params: dict) -> dict:
    return {
        "tipo": params.get("tipo", ""),
        "severidad": params.get("severidad", ""),
        "descripcion": params.get("descripcion", ""),
    }


def _ctx_disponibilidad(db: Session, params: dict) -> dict:
    fecha_str = params.get("fecha", str(date.today()))
    turno     = params.get("turno", "")
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        fecha = date.today()

    q = (
        db.query(Asignacion)
        .join(HorarioServicio)
        .filter(
            HorarioServicio.fecha == fecha,
            Asignacion.estado.in_(["propuesta", "confirmada"]),
        )
    )
    if turno:
        q = q.filter(HorarioServicio.turno == turno)
    ocupados_ids = {a.chofer_id for a in q.all()}
    no_disponibles_ids = {
        d.chofer_id
        for d in db.query(DisponibilidadChofer)
        .filter(DisponibilidadChofer.fecha == fecha)
        .all()
    }
    excluir = ocupados_ids | no_disponibles_ids

    disponibles = (
        db.query(Chofer)
        .filter(Chofer.estado == "activo", ~Chofer.id.in_(excluir))
        .all()
    )
    return {
        "fecha": fecha_str,
        "turno": turno or "cualquier turno",
        "total_disponibles": len(disponibles),
        "choferes": ", ".join(
            f"{c.nombres} {c.apellidos}" for c in disponibles[:10]
        ) or "ninguno",
    }


def _ctx_explicar_alerta(db: Session, params: dict) -> dict:
    alertas = detectar_alertas_fatiga(db)
    if not alertas:
        return {"info": "No se detectaron alertas de fatiga esta semana."}
    resumen = [
        {
            "chofer": f"{a['nombres']} {a['apellidos']}",
            "tipo": a["tipo"].replace("_", " "),
            "detalle": a["detalle"],
        }
        for a in alertas
    ]
    return {"total_alertas": len(alertas), "alertas": resumen}


def _ctx_horas_area(db: Session, params: dict) -> dict:
    lunes = _inicio_semana(date.today())
    dom   = lunes + timedelta(days=6)

    areas = db.query(AreaOperativa).all()
    resumen = []
    for area in areas:
        asigs = (
            db.query(Asignacion)
            .join(HorarioServicio)
            .filter(
                Asignacion.area_id == area.id,
                Asignacion.estado.in_(["propuesta", "confirmada"]),
                HorarioServicio.fecha.between(lunes, dom),
            )
            .all()
        )
        total_min = sum(a.horario.duracion_est_min for a in asigs)
        resumen.append({
            "area": area.nombre,
            "horas_asignadas": round(total_min / 60, 1),
            "total_asignaciones": len(asigs),
        })
    return {"semana": f"{lunes} al {dom}", "areas": resumen}


def _ctx_estado_programacion(db: Session, params: dict) -> dict:
    progs = (
        db.query(Programacion)
        .order_by(Programacion.fecha_inicio.desc())
        .limit(5)
        .all()
    )
    if not progs:
        return {"info": "No hay programaciones registradas."}
    return {
        "programaciones": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "estado": p.estado,
                "fecha_inicio": str(p.fecha_inicio),
                "fecha_fin": str(p.fecha_fin),
                "total_horarios": len(p.horarios_servicio),
                "total_asignaciones": sum(len(h.asignaciones) for h in p.horarios_servicio),
            }
            for p in progs
        ]
    }
