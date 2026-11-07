"""
src/api/webhook_server.py
Servidor FastAPI que recebe as mensagens do WhatsApp (Z-API / Evolution Webhook)
e executa o Scheduler de segundo plano em conjunto.
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
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
    return {"status": "online", "app": "Vai na Boa", "whatsapp": "Z-API conectado"}


@app.post("/webhook/zapi")
async def webhook_zapi(request: Request):
    """
    Endpoint chamado pela Z-API sempre que uma mensagem chega no WhatsApp.
    """
    try:
        dados = await request.json()

        # Ignora mensagens enviadas por você mesmo
        if dados.get("fromMe", False):
            return {"status": "ignorado", "motivo": "fromMe"}

        remetente = dados.get("phone", "")
        # Extrai o texto da mensagem
        texto = dados.get("text", {}).get("message", "") or dados.get("message", "")

        if not texto.strip():
            return {"status": "ignorado", "motivo": "sem texto"}

        print(f"\n📩 [Mensagem Recebida via Z-API de {remetente}]: {texto}")

        # Processa a resposta no cérebro do Vai na Boa
        resposta = processar_mensagem_whatsapp(texto)

        # Envia a resposta de volta para o seu WhatsApp
        enviar_mensagem_whatsapp(resposta, numero=remetente)

        return {"status": "sucesso", "resposta_enviada": True}

    except Exception as err:
        print(f"❌ [Webhook Z-API] Erro: {err}")
        return {"status": "erro", "detalhes": str(err)}


# Mantem compatibilidade com endpoint evolution
@app.post("/webhook/evolution")
async def webhook_evolution(request: Request):
    return await webhook_zapi(request)


if __name__ == "__main__":
    uvicorn.run("api.webhook_server:app", host="0.0.0.0", port=8000, reload=False)
