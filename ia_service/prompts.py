import json

SISTEMA_BASE = (
    "Eres el asistente inteligente de MetroHub, el sistema de programación "
    "de horarios del Metropolitano de Lima. Responde siempre en español, "
    "de forma clara y concisa."
)


def prompt_reemplazo(horario: dict, candidatos: list[dict], chofer_ausente: dict) -> str:
    candidatos_texto = "\n".join([
        f"  - ID {c['chofer_id']}: {c['nombres']} {c['apellidos']}: "
        f"{c['horas_semana']:.1f}h trabajadas esta semana, "
        f"{c['turnos_noche_consecutivos']} turnos noche consecutivos"
        for c in candidatos
    ])
    return (
        f"{SISTEMA_BASE}\n\n"
        f"Se necesita cubrir urgentemente el siguiente turno:\n"
        f"  Fecha: {horario['fecha']}\n"
        f"  Hora de salida: {horario['hora_salida']}\n"
        f"  Turno: {horario['turno']}\n"
        f"  Ruta: {horario['ruta_nombre']}\n\n"
        f"El chofer ausente es: {chofer_ausente['nombres']} {chofer_ausente['apellidos']} "
        f"(motivo: {chofer_ausente.get('motivo', 'no especificado')}).\n\n"
        f"Candidatos disponibles y válidos:\n{candidatos_texto}\n\n"
        f"Recomienda al mejor candidato considerando menor carga horaria y "
        f"menor riesgo de fatiga. Responde ÚNICAMENTE con este JSON (sin markdown ni texto extra):\n"
        f'{{"chofer_id": <id numérico del candidato recomendado>, '
        f'"recomendacion": "<máximo 3 oraciones explicando tu elección>"}}'
    )


def prompt_alertas_fatiga(alertas: list[dict]) -> str:
    alertas_texto = "\n".join([
        f"  Chofer: {a['nombres']} {a['apellidos']} | "
        f"Tipo: {a['tipo']} | Detalle: {a['detalle']}"
        for a in alertas
    ])
    return (
        f"{SISTEMA_BASE}\n\n"
        f"Analiza las siguientes situaciones de riesgo detectadas en la programación:\n"
        f"{alertas_texto}\n\n"
        f"Para cada caso (en el MISMO ORDEN que se presentaron) genera exactamente este JSON "
        f"(sin markdown, solo el array):\n"
        f'[{{"alerta": "texto alerta max 2 líneas", '
        f'"sugerencia": "acción concreta max 1 línea", '
        f'"severidad": "baja|media|alta"}}, ...]\n\n'
        f"Criterio de severidad: alta=descanso insuficiente o >50h semana, "
        f"media=turnos noche consecutivos >3 o 40-50h semana, baja=resto."
    )


def prompt_chat(intent: str, contexto: dict, pregunta: str) -> str:
    if intent == "resolver_conflicto":
        tipo = contexto.get("tipo", "").replace("_", " ")
        sev  = contexto.get("severidad", "")
        desc = contexto.get("descripcion", "")
        return (
            f"{SISTEMA_BASE}\n\n"
            f"El administrador necesita resolver el siguiente conflicto de programación:\n"
            f"  Tipo: {tipo}\n"
            f"  Severidad: {sev}\n"
            f"  Descripción: {desc}\n\n"
            f"Proporciona 2-3 pasos concretos y prácticos para resolverlo. "
            f"Sé directo. Usa párrafos cortos, sin bullets."
        )
    contexto_texto = json.dumps(contexto, ensure_ascii=False, indent=2)
    return (
        f"{SISTEMA_BASE}\n\n"
        f"El usuario pregunta: \"{pregunta}\"\n\n"
        f"Datos actuales del sistema:\n{contexto_texto}\n\n"
        f"Usa los datos para responder de forma directa y útil. "
        f"Máximo 4 oraciones. Si el usuario menciona un nombre o área específica, "
        f"búscala en los datos. Si la información no alcanza para responder con certeza, indícalo."
    )
