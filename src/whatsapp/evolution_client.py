"""
src/whatsapp/evolution_client.py
Cliente Unificado de envio de WhatsApp.
Envia prioritariamente via Z-API se configurada, ou via Evolution API.
"""
import os
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from whatsapp.zapi_client import enviar_mensagem_whatsapp as enviar_zapi


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Roteador de envio: envia direto pela Z-API conectada.
    """
    return enviar_zapi(texto, numero)
