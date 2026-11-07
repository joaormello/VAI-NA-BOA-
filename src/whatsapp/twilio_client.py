"""
src/whatsapp/twilio_client.py
Cliente para envio de mensagens via WhatsApp oficial da Twilio (Sandbox).
"""
import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
DESTINATARIO_PADRAO = os.getenv("WHATSAPP_NUMERO_DESTINO", "")


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Envia uma mensagem de WhatsApp via API oficial da Twilio.
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("[Aviso] [Twilio] TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN nao configurados no .env!")
        return False

    alvo = numero or DESTINATARIO_PADRAO
    if not alvo:
        print("[Aviso] [Twilio] Nenhum numero de destino configurado!")
        return False

    # Garante o prefixo whatsapp:+55...
    alvo_limpo = "".join(filter(str.isdigit, alvo))
    destinatario = f"whatsapp:+{alvo_limpo}" if not alvo.startswith("whatsapp:") else alvo

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

    data = {
        "From": TWILIO_WHATSAPP_NUMBER,
        "To": destinatario,
        "Body": texto,
    }

    try:
        resp = requests.post(
            url,
            data=data,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
        resp.raise_for_status()
        print(f"✅ [Twilio] Mensagem enviada com sucesso para {destinatario}!")
        return True
    except Exception as err:
        print(f"[Erro] [Twilio] Falha ao enviar para {destinatario}: {err}")
        return False
