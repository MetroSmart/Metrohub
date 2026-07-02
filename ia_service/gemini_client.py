import json
import os

import requests

_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_MODEL   = "llama-3.3-70b-versatile"


def _llamar(prompt: str, max_tokens: int) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada")
    resp = requests.post(
        _API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": _MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generar_texto(prompt: str) -> str:
    try:
        return _llamar(prompt, max_tokens=512)
    except Exception as e:
        raise ValueError(f"Groq API: {e}") from e


def generar_json(prompt: str):
    try:
        texto = _llamar(prompt, max_tokens=1024)
    except Exception as e:
        raise ValueError(f"Groq API: {e}") from e
    if texto.startswith("```"):
        texto = texto.split("```")[1].strip()
        if texto.startswith("json"):
            texto = texto[4:]
    return json.loads(texto.strip())
