"""
src/api/webhook_server.py
Servidor FastAPI unificado:
- Webhook Telegram (/webhook/telegram)
- Webhook Twilio WhatsApp (/webhook/twilio)
- Webhook Z-API (/webhook/zapi)
- Inicia o Scheduler de segundo plano automaticamente
"""
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn

BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from whatsapp.bot_handler import processar_mensagem_whatsapp
from telegram.telegram_client import enviar_mensagem_telegram
from whatsapp.evolution_client import enviar_mensagem_whatsapp
from scheduler.routine_scheduler import iniciar_agendador

app = FastAPI(title="Vai na Boa - Bot Server")


@app.on_event("startup")
def startup_event():
    iniciar_agendador()


@app.get("/")
def health_check():
    return {
        "status": "online",
        "app": "Vai na Boa",
        "telegram": "@VAI_BOA_BOT conectado",
        "rotas": "Google Routes Live Ativo",
    }


@app.post("/webhook/telegram")
async def webhook_telegram(request: Request):
    """
    Endpoint chamado pelo Telegram sempre que voce envia mensagem para o @VAI_BOA_BOT.
    """
    try:
        dados = await request.json()
        message = dados.get("message", {})
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        texto = message.get("text", "").strip()

        if not chat_id or not texto:
            return {"status": "ignorado"}

        print(f"\n📩 [Telegram Recebido de {chat_id}]: {texto}")

        # Se você ainda não cadastrou o TELEGRAM_CHAT_ID no Render, loga o seu ID na hora!
        print(f"👉 [SEU TELEGRAM CHAT_ID É: {chat_id}]")

        # Processa a resposta no cérebro do Vai na Boa
        resposta = processar_mensagem_whatsapp(texto)

        # Envia de volta para você no Telegram
        enviar_mensagem_telegram(resposta, chat_id=chat_id)

        return {"status": "ok"}
    except Exception as err:
        print(f"❌ [Webhook Telegram] Erro: {err}")
        return {"status": "erro", "detalhes": str(err)}


@app.post("/webhook/twilio")
async def webhook_twilio(request: Request):
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace")
        form_data = parse_qs(body_str)

        remetente = form_data.get("From", [""])[0]
        texto = form_data.get("Body", [""])[0].strip()

        if not texto:
            return PlainTextResponse("")

        resposta = processar_mensagem_whatsapp(texto)
        resposta_xml = (
            resposta.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{resposta_xml}</Message>
</Response>"""
        return Response(content=twiml_response, media_type="application/xml")
    except Exception as err:
        return PlainTextResponse(f"Erro: {err}", status_code=500)


@app.post("/webhook/zapi")
async def webhook_zapi(request: Request):
    try:
        dados = await request.json()
        if dados.get("fromMe", False):
            return {"status": "ignorado"}
        remetente = dados.get("phone", "")
        texto = dados.get("text", {}).get("message", "") or dados.get("message", "")
        if texto:
            resposta = processar_mensagem_whatsapp(texto)
            enviar_mensagem_whatsapp(resposta, numero=remetente)
        return {"status": "ok"}
    except Exception as err:
        return {"status": "erro", "detalhes": str(err)}


if __name__ == "__main__":
    uvicorn.run("api.webhook_server:app", host="0.0.0.0", port=8000, reload=False)
