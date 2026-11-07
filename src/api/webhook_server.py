"""
src/api/webhook_server.py
Servidor FastAPI que recebe as mensagens do WhatsApp (Twilio Webhook / Z-API)
e responde tanto via TwiML nativo quanto via API de envio.
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn

BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from whatsapp.bot_handler import processar_mensagem_whatsapp
from whatsapp.evolution_client import enviar_mensagem_whatsapp
from scheduler.routine_scheduler import iniciar_agendador

app = FastAPI(title="Vai na Boa - WhatsApp Webhook")


@app.on_event("startup")
def startup_event():
    iniciar_agendador()


@app.get("/")
def health_check():
    return {"status": "online", "app": "Vai na Boa", "whatsapp": "Twilio / Z-API conectado"}


@app.post("/webhook/twilio")
async def webhook_twilio(request: Request):
    """
    Endpoint chamado pela Twilio ao receber mensagem no WhatsApp.
    Responde diretamente via TwiML (resposta sincrona instantanea)
    para nao depender de credenciais REST adicionais no envio!
    """
    try:
        form = await request.form()
        remetente = form.get("From", "")
        texto = form.get("Body", "").strip()

        print(f"\n📩 [Twilio Recebido de {remetente}]: {texto}")

        if not texto:
            return PlainTextResponse("")

        # Processa a resposta no cérebro do Vai na Boa
        resposta = processar_mensagem_whatsapp(texto)
        print(f"🤖 [Resposta Gerada]:\n{resposta}")

        # Responde com TwiML nativo do WhatsApp (metodo oficial e instantaneo da Twilio)
        # Escapa caracteres XML basicos
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
        print(f"❌ [Webhook Twilio] Erro: {err}")
        return PlainTextResponse("")


@app.post("/webhook/zapi")
async def webhook_zapi(request: Request):
    try:
        dados = await request.json()
        if dados.get("fromMe", False):
            return {"status": "ignorado", "motivo": "fromMe"}

        remetente = dados.get("phone", "")
        texto = dados.get("text", {}).get("message", "") or dados.get("message", "")

        if not texto.strip():
            return {"status": "ignorado", "motivo": "sem texto"}

        resposta = processar_mensagem_whatsapp(texto)
        enviar_mensagem_whatsapp(resposta, numero=remetente)
        return {"status": "sucesso"}
    except Exception as err:
        return {"status": "erro", "detalhes": str(err)}


if __name__ == "__main__":
    uvicorn.run("api.webhook_server:app", host="0.0.0.0", port=8000, reload=False)
