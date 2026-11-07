"""
src/whatsapp/evolution_client.py
Cliente HTTP para envio de mensagens via Evolution API.
"""
import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "vai_na_boa")
DESTINATARIO_PADRAO = os.getenv("WHATSAPP_NUMERO_DESTINO", "")


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Envia uma mensagem de texto para um número de WhatsApp via Evolution API.
    O número deve estar no formato DDI + DDD + Telefone (ex: 5511999999999).
    """
    alvo = numero or DESTINATARIO_PADRAO
    if not alvo:
        print("[Aviso] [Evolution API] Nenhum número de destino configurado no .env!")
        return False

    alvo_limpo = "".join(filter(str.isdigit, alvo))

    url = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "number": alvo_limpo,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": True,
        },
        "textMessage": {
            "text": texto,
        },
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as err:
        print(f"[Erro] [Evolution API] Falha ao enviar para {alvo_limpo}: {err}")
        return False
