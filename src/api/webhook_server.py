"""
src/api/webhook_server.py
Servidor FastAPI que recebe as mensagens do WhatsApp (Evolution API Webhook)
e executa o Scheduler de segundo plano em conjunto.
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
import uvicorn

# Garante importações a partir de src/
BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from whatsapp.bot_handler import processar_mensagem_whatsapp
from whatsapp.evolution_client import enviar_mensagem_whatsapp
from scheduler.routine_scheduler import iniciar_agendador

app = FastAPI(title="Vai na Boa - WhatsApp Webhook")


@app.on_event("startup")
def startup_event():
    # Inicia o agendador do Apple Watch / WhatsApp assim que o servidor liga
    iniciar_agendador()


@app.get("/")
def health_check():
    return {"status": "online", "app": "Vai na Boa"}


@app.post("/webhook/evolution")
async def webhook_evolution(request: Request):
    """
    Endpoint chamado pela Evolution API sempre que uma mensagem chega no WhatsApp.
    """
    try:
        dados = await request.json()
        evento = dados.get("event")

        # Só processa se for mensagem recebida (messages.upsert)
        if evento != "messages.upsert":
            return {"status": "ignorado", "motivo": f"evento {evento}"}

        msg_data = dados.get("data", {})
        key = msg_data.get("key", {})

        # Ignora mensagens enviadas pelo próprio bot
        if key.get("fromMe", False):
            return {"status": "ignorado", "motivo": "fromMe"}

        remetente = key.get("remoteJid", "").split("@")[0]

        # Extrai o texto da mensagem recebida
        message_content = msg_data.get("message", {})
        texto = (
            message_content.get("conversation")
            or message_content.get("extendedTextMessage", {}).get("text")
            or ""
        )

        if not texto.strip():
            return {"status": "ignorado", "motivo": "sem texto"}

        print(f"\n📩 [Mensagem Recebida de {remetente}]: {texto}")

        # Processa a resposta no cérebro do Vai na Boa
        resposta = processar_mensagem_whatsapp(texto)

        # Envia a resposta de volta para o usuário no WhatsApp
        enviar_mensagem_whatsapp(resposta, numero=remetente)

        return {"status": "sucesso", "resposta_enviada": True}

    except Exception as err:
        print(f"❌ [Webhook] Erro ao processar webhook: {err}")
        return {"status": "erro", "detalhes": str(err)}


if __name__ == "__main__":
    uvicorn.run("api.webhook_server:app", host="0.0.0.0", port=8000, reload=False)
