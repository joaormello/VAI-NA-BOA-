"""
src/whatsapp/evolution_client.py
Roteador unificado de envio de WhatsApp.
Envia prioritariamente via Twilio Sandbox (numero independente) se configurado,
ou via Z-API / Evolution.
"""
import os
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from whatsapp.twilio_client import enviar_mensagem_whatsapp as enviar_twilio
from whatsapp.zapi_client import enviar_mensagem_whatsapp as enviar_zapi


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Roteador de envio: usa Twilio se as credenciais existirem, senao Z-API.
    """
    if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
        return enviar_twilio(texto, numero)
    return enviar_zapi(texto, numero)
