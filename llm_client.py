"""
llm_client.py
Cliente para el modelo de lenguaje (Gemini). Encapsula la llamada al LLM
para facilitar el cambio de proveedor en el futuro.
"""

import os
from typing import Optional

# Carga de variables de entorno (debe llamarse antes de usar la API)
from dotenv import load_dotenv

load_dotenv()

# Proveedor actual: Google Generative AI (Gemini)
try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _get_api_key() -> Optional[str]:
    """Obtiene la API key desde el entorno. Nunca se incluye en el código."""
    return os.getenv("GEMINI_API_KEY")


def _get_client():
    """Configura y devuelve el cliente de Gemini. None si no está disponible."""
    if genai is None:
        return None
    api_key = _get_api_key()
    if not api_key or not api_key.strip():
        return None
    genai.configure(api_key=api_key.strip())
    return genai


def generate_analysis(context: str) -> tuple[bool, str]:
    """
    Genera el análisis de trading a partir del contexto estructurado.
    
    Args:
        context: Texto con datos técnicos, titulares, perfil de riesgo y horizonte.
    
    Returns:
        Tupla (éxito: bool, mensaje: str). Si éxito es False, mensaje describe el error.
    """
    client = _get_client()
    if client is None:
        if genai is None:
            return False, "Error: Falta instalar google-generativeai. Ver requirements.txt."
        return False, "Error: GEMINI_API_KEY no configurada. Crea un archivo .env con tu API key."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            context,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
            },
        )
        if not response or not response.text:
            return False, "Error: El modelo no devolvió texto. Intenta de nuevo."
        return True, response.text.strip()
    except Exception as e:
        err_msg = str(e).strip() or "Error desconocido"
        if "API_KEY" in err_msg.upper() or "invalid" in err_msg.lower():
            return False, "Error: API key inválida o no autorizada. Revisa tu .env."
        if "quota" in err_msg.lower() or "resource" in err_msg.lower():
            return False, "Error: Límite de uso de la API alcanzado. Intenta más tarde."
        return False, f"Error de API: {err_msg}"
