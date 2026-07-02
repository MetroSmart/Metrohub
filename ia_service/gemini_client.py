import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def _get_model():
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model


def generar_texto(prompt: str) -> str:
    model = _get_model()
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise ValueError(f"Gemini API: {e}") from e


def generar_json(prompt: str):
    model = _get_model()
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        raise ValueError(f"Gemini API: {e}") from e
    texto = response.text.strip()
    if texto.startswith("```"):
        # split por ``` y tomar el segmento interior; .strip() elimina \n inicial
        texto = texto.split("```")[1].strip()
        if texto.startswith("json"):
            texto = texto[4:]
    return json.loads(texto.strip())
