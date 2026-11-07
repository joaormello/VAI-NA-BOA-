"""
src/whatsapp/zapi_client.py
Cliente HTTP para envio de mensagens via Z-API.
"""
import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "01A1B7C017817EFDA8EE9E4C065F20EF")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "60591EA7FFC6AFF0C7D1997C")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")
DESTINATARIO_PADRAO = os.getenv("WHATSAPP_NUMERO_DESTINO", "")

# Base URL da Z-API
ZAPI_BASE_URL = os.getenv("ZAPI_BASE_URL", "https://api.z-api.io")


def enviar_mensagem_whatsapp(texto: str, numero: str = None) -> bool:
    """
    Envia uma mensagem de texto via Z-API.
    Formato do telefone: DDI + DDD + Telefone (ex: 5511999999999).
    """
    alvo = numero or DESTINATARIO_PADRAO
    if not alvo:
        print("[Aviso] [Z-API] Nenhum número de destino configurado!")
        return False

    alvo_limpo = "".join(filter(str.isdigit, alvo))

    # Endpoint padrão da Z-API para envio de texto
    url = f"{ZAPI_BASE_URL.rstrip('/')}/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

    headers = {
        "Content-Type": "application/json",
    }
    if ZAPI_CLIENT_TOKEN:
        headers["Client-Token"] = ZAPI_CLIENT_TOKEN

    payload = {
        "phone": alvo_limpo,
        "message": texto,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        print(f"✅ [Z-API] Mensagem enviada com sucesso para {alvo_limpo}!")
        return True
    except Exception as err:
        print(f"[Erro] [Z-API] Falha ao enviar para {alvo_limpo}: {err}")
        return False
