"""
src/scheduler/routine_scheduler.py
Agendador automático em background (Despertador do Apple Watch / WhatsApp).
Verifica a cada minuto os compromissos do dia e dispara:
1. Pergunta de origem (45 min antes, se houver múltiplas opções)
2. Escadinha no relógio: 30, 15, 10, 5 min antes e 0 min (SAIA AGORA!)
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler

# Garante importações a partir de src/
BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from database.appointments_repository import listar_compromissos_do_dia
from services.routine_service import verificar_eventos_compromisso
from whatsapp.evolution_client import enviar_mensagem_whatsapp


def verificar_rotina_do_minuto():
    """
    Roda a cada 60 segundos. Avalia os compromissos de hoje e dispara os alertas devidos.
    """
    agora = datetime.now()
    compromissos = listar_compromissos_do_dia(agora)

    if not compromissos:
        return []

    eventos_gerados = []

    for comp in compromissos:
        eventos = verificar_eventos_compromisso(comp, agora=agora, tolerancia_janela_min=2)
        for ev in eventos:
            eventos_gerados.append(ev)
            _enviar_notificacao_whatsapp(ev["mensagem"])

    return eventos_gerados


def _enviar_notificacao_whatsapp(mensagem: str):
    """
    Ponto central de envio da notificação:
    1. Envia via Evolution API direto pro seu WhatsApp / Apple Watch
    2. Imprime no terminal para acompanhamento visual
    """
    agora = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{agora}] 🔔 [DISPARO NO SEU APPLE WATCH / WHATSAPP]")
    print(mensagem)
    print("-" * 60)

    # Dispara mensagem via Evolution API
    enviar_mensagem_whatsapp(mensagem)


def iniciar_agendador():
    """
    Inicia o scheduler em segundo plano.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(verificar_rotina_do_minuto, "interval", seconds=60, id="job_rotina_minuto")
    scheduler.start()
    print("⏰ [Vai na Boa] Agendador de rotina ativado! Verificando a cada 60 segundos...")
    return scheduler


if __name__ == "__main__":
    print("Iniciando Agendador de Teste do Vai na Boa...")
    sched = iniciar_agendador()

    verificar_rotina_do_minuto()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nDesligando agendador...")
        sched.shutdown()
