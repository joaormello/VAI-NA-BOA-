"""
src/telegram/telegram_client.py
Cliente para envio de mensagens via Telegram Bot API nativa.
"""
import os
import sys
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9215294037:AAHOiGgFYNFm56gYmltZL1lcFckCHWBlSyc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def enviar_mensagem_telegram(texto: str, chat_id: str = None) -> bool:
    """
    Envia uma mensagem de texto para o usuário via Telegram Bot.
    """
    alvo = chat_id or TELEGRAM_CHAT_ID
    if not alvo:
        print("[Aviso] [Telegram] Nenhum TELEGRAM_CHAT_ID configurado!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": alvo,
        "text": texto,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10, verify=False)
        resp.raise_for_status()
        print(f"✅ [Telegram] Mensagem enviada com sucesso para chat_id {alvo}!")
        return True
    except Exception as err:
        print(f"[Erro] [Telegram] Falha ao enviar para {alvo}: {err}")
        return False
