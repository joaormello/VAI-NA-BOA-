"""
src/whatsapp/evolution_client.py
Roteador unificado de envio de notificacoes do Vai na Boa:
1. Envia via Telegram se TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID existirem.
2. Senao, envia via WhatsApp (Twilio / Z-API).
"""
import os
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from telegram.telegram_client import enviar_mensagem_telegram
from whatsapp.twilio_client import enviar_mensagem_whatsapp as enviar_twilio
from whatsapp.zapi_client import enviar_mensagem_whatsapp as enviar_zapi


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Roteador de envio universal:
    Se configurado o Telegram, dispara prioritariamente para ele (Apple Watch e celular).
    """
    if os.getenv("TELEGRAM_BOT_TOKEN") and (numero or os.getenv("TELEGRAM_CHAT_ID")):
        return enviar_mensagem_telegram(texto, chat_id=numero)

    if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
        return enviar_twilio(texto, numero)

    return enviar_zapi(texto, numero)
