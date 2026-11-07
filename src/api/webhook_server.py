"""
src/api/webhook_server.py
Servidor FastAPI que recebe as mensagens do WhatsApp (Twilio Webhook / Z-API)
e executa o Scheduler de segundo plano em conjunto.
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
    Endpoint chamado pela Twilio sempre que voce envia uma mensagem para o Bot Oficial no WhatsApp.
    Recebe os dados via form-urlencoded padrao da Twilio.
    """
    try:
        form = await request.form()
        remetente = form.get("From", "")  # Ex: whatsapp:+5511999999999
        texto = form.get("Body", "").strip()

        if not texto:
            return PlainTextResponse("")

        print(f"\n📩 [Mensagem Recebida via Twilio de {remetente}]: {texto}")

        # Processa a resposta no cérebro do Vai na Boa
        resposta = processar_mensagem_whatsapp(texto)

        # Envia de volta para o seu WhatsApp atraves da Twilio
        enviar_mensagem_whatsapp(resposta, numero=remetente)

        return PlainTextResponse("")

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


@app.post("/webhook/evolution")
async def webhook_evolution(request: Request):
    return await webhook_zapi(request)


if __name__ == "__main__":
    uvicorn.run("api.webhook_server:app", host="0.0.0.0", port=8000, reload=False)
