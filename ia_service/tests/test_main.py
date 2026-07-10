"""Tests del microservicio IA (puerto 8001) con mock del cliente Groq.

Nunca se llama a la API real: se hace monkeypatch de generar_json/generar_texto
en el namespace de main (donde fueron importados). Cubre los 4 endpoints y los
fallbacks determinísticos cuando la IA falla o responde basura.
"""
import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)

CANDIDATOS = [
    {"chofer_id": 1, "nombres": "Juan", "apellidos": "Huamán",
     "horas_semana": 30.0, "turnos_noche_consecutivos": 2},
    {"chofer_id": 2, "nombres": "Rosa", "apellidos": "Quispe",
     "horas_semana": 12.0, "turnos_noche_consecutivos": 0},
]

REEMPLAZO_REQ = {
    "horario": {"fecha": "2026-07-13", "hora_salida": "08:00",
                "turno": "manana", "ruta_nombre": "Naranjal - Matellini"},
    "candidatos": CANDIDATOS,
    "chofer_ausente": {"nombres": "Pedro", "apellidos": "Salas", "motivo": "descanso médico"},
}

ALERTAS_REQ = {
    "alertas": [
        {"chofer_id": 1, "nombres": "Juan", "apellidos": "Huamán",
         "tipo": "exceso_horas_semana", "detalle": {"horas_asignadas": 56.0}},
        {"chofer_id": 2, "nombres": "Rosa", "apellidos": "Quispe",
         "tipo": "descanso_insuficiente", "detalle": {"descanso_horas": 2.0}},
    ]
}


# ── /health ───────────────────────────────────────────────
def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── /reemplazo ────────────────────────────────────────────
def test_reemplazo_sin_candidatos_400():
    resp = client.post("/reemplazo", json={**REEMPLAZO_REQ, "candidatos": []})
    assert resp.status_code == 400


def test_reemplazo_ok_con_ia(monkeypatch):
    monkeypatch.setattr(main, "generar_json",
                        lambda p: {"chofer_id": 1, "recomendacion": "Es el más experimentado."})
    resp = client.post("/reemplazo", json=REEMPLAZO_REQ)
    assert resp.status_code == 200
    body = resp.json()
    assert body["chofer_id_recomendado"] == 1
    assert body["recomendacion"] == "Es el más experimentado."


def test_reemplazo_fallback_si_ia_recomienda_invalido(monkeypatch):
    # la IA devuelve un chofer fuera de la lista → gana el de menor carga (2)
    monkeypatch.setattr(main, "generar_json",
                        lambda p: {"chofer_id": 999, "recomendacion": "x"})
    resp = client.post("/reemplazo", json=REEMPLAZO_REQ)
    assert resp.status_code == 200
    assert resp.json()["chofer_id_recomendado"] == 2


def test_reemplazo_fallback_si_groq_caido(monkeypatch):
    def _boom(p):
        raise ValueError("Groq API: connection refused")
    monkeypatch.setattr(main, "generar_json", _boom)
    resp = client.post("/reemplazo", json=REEMPLAZO_REQ)
    assert resp.status_code == 200
    body = resp.json()
    assert body["chofer_id_recomendado"] == 2
    assert "menor carga" in body["recomendacion"]


# ── /alertas-fatiga ───────────────────────────────────────
def test_alertas_vacias():
    resp = client.post("/alertas-fatiga", json={"alertas": []})
    assert resp.status_code == 200
    assert resp.json() == {"alertas": []}


def test_alertas_ok_con_ia(monkeypatch):
    monkeypatch.setattr(main, "generar_json", lambda p: [
        {"alerta": "Sobrecarga", "sugerencia": "Redistribuir", "severidad": "alta"},
        {"alerta": "Poco descanso", "sugerencia": "Espaciar turnos", "severidad": "media"},
    ])
    resp = client.post("/alertas-fatiga", json=ALERTAS_REQ)
    assert resp.status_code == 200
    alertas = resp.json()["alertas"]
    assert len(alertas) == 2
    assert alertas[0]["chofer_id"] == 1
    assert alertas[0]["alerta"] == "Sobrecarga"
    assert alertas[1]["severidad"] == "media"


def test_alertas_fallback_por_tipo(monkeypatch):
    def _boom(p):
        raise ValueError("Groq API caída")
    monkeypatch.setattr(main, "generar_json", _boom)
    resp = client.post("/alertas-fatiga", json=ALERTAS_REQ)
    assert resp.status_code == 200
    alertas = resp.json()["alertas"]
    assert alertas[0]["alerta"] == "Exceso de horas semanales detectado."
    assert alertas[0]["severidad"] == "alta"
    assert alertas[1]["alerta"] == "Descanso insuficiente entre turnos consecutivos."


def test_alertas_fallback_si_respuesta_no_es_lista(monkeypatch):
    monkeypatch.setattr(main, "generar_json", lambda p: {"no": "es lista"})
    resp = client.post("/alertas-fatiga", json=ALERTAS_REQ)
    assert resp.status_code == 200
    assert len(resp.json()["alertas"]) == 2  # usó los textos de fallback


# ── /chat ─────────────────────────────────────────────────
def test_chat_ok(monkeypatch):
    monkeypatch.setattr(main, "generar_texto", lambda p: "Hay 3 choferes disponibles.")
    resp = client.post("/chat", json={"intent": "disponibilidad",
                                      "contexto": {"total_disponibles": 3},
                                      "pregunta": "¿Quién está libre?"})
    assert resp.status_code == 200
    assert resp.json()["respuesta"] == "Hay 3 choferes disponibles."


def test_chat_502_si_groq_caido(monkeypatch):
    def _boom(p):
        raise ValueError("Groq API: timeout")
    monkeypatch.setattr(main, "generar_texto", _boom)
    resp = client.post("/chat", json={"intent": "disponibilidad",
                                      "contexto": {}, "pregunta": "¿?"})
    assert resp.status_code == 502
