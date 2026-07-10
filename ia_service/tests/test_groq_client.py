"""Tests unitarios de groq_client (parseo de respuestas y manejo de errores)."""
import pytest

import groq_client


def test_generar_texto_sin_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        groq_client.generar_texto("hola")


def test_generar_json_parsea_fence_markdown(monkeypatch):
    monkeypatch.setattr(groq_client, "_llamar",
                        lambda prompt, max_tokens: '```json\n{"chofer_id": 5}\n```')
    assert groq_client.generar_json("p") == {"chofer_id": 5}


def test_generar_json_parsea_json_plano(monkeypatch):
    monkeypatch.setattr(groq_client, "_llamar",
                        lambda prompt, max_tokens: '[{"a": 1}]')
    assert groq_client.generar_json("p") == [{"a": 1}]


def test_generar_json_error_de_red_lanza_valueerror(monkeypatch):
    def _boom(prompt, max_tokens):
        raise ConnectionError("refused")
    monkeypatch.setattr(groq_client, "_llamar", _boom)
    with pytest.raises(ValueError, match="Groq API"):
        groq_client.generar_json("p")
