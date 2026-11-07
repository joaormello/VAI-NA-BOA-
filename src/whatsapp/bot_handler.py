"""
src/whatsapp/bot_handler.py
Interpretador central de mensagens e comandos do WhatsApp / Apple Watch.
"""
from datetime import datetime
from database.appointments_repository import (
    listar_compromissos_do_dia,
    obter_ou_criar_estado_diario,
)
from services.routine_service import (
    calcular_opcoes_saida_compromisso,
    processar_resposta_origem,
)
from services.feedback_service import registrar_feedback_chegada


def processar_mensagem_whatsapp(texto_recebido: str) -> str:
    """
    Recebe o texto enviado pelo usuário e retorna a resposta formatada.
    """
    msg = texto_recebido.strip()
    msg_lower = msg.lower()

    # 1. Feedback de chegada (Ex: "cheguei no horário", "cheguei 15 min atrasado")
    if "cheguei" in msg_lower or "atrasei" in msg_lower:
        return _tratar_feedback_chegada(msg)

    # 2. Resposta de número de origem (Ex: o bot perguntou e o usuário respondeu "1" ou "2")
    if msg.isdigit() and len(msg) <= 2:
        return _tratar_resposta_origem(msg)

    # 3. Comandos com barra ou palavras-chave
    if msg_lower in ("/status", "/rotina", "status", "rotina"):
        return _gerar_resumo_status_hoje()

    if msg_lower in ("/sair", "/sair-agora", "sair", "sair agora"):
        return _gerar_orientacao_saida_imediata()

    if msg_lower in ("/ajuda", "ajuda", "help", "oi", "ola", "olá"):
        return _menu_ajuda()

    # Resposta padrão caso não entenda
    return (
        "🤖 Não entendi esse comando.\n\n"
        "Envie */status* para ver seus compromissos de hoje,\n"
        "*/sair* para ver a próxima saída,\n"
        "ou */ajuda* para ver todas as opções."
    )


def _gerar_resumo_status_hoje() -> str:
    """
    Monta o relatório dos compromissos cadastrados para hoje.
    """
    hoje = datetime.now()
    compromissos = listar_compromissos_do_dia(hoje)

    if not compromissos:
        return (
            f"📅 *Rotina de Hoje ({hoje.strftime('%d/%m')})*\n\n"
            "Nenhum compromisso agendado para hoje. Vai na boa e descanse! 🏖️"
        )

    linhas = [f"📅 *Sua Rotina de Hoje ({hoje.strftime('%d/%m')})*:\n"]

    for comp in compromissos:
        estado = obter_ou_criar_estado_diario(comp["id"], hoje.strftime("%Y-%m-%d"))
        opcoes = calcular_opcoes_saida_compromisso(comp)

        # Se o usuário já escolheu a origem hoje, pega a opção correspondente
        origem_id = estado["origem_escolhida_id"] or comp["origem_id"]
        opcao = next((o for o in opcoes if o["origem_id"] == origem_id), opcoes[0])

        modal_info = ""
        if opcao.get("melhor_modal"):
            modal_info = f" ({opcao['melhor_modal']['icone']} {opcao['melhor_modal']['descricao']})"

        linhas.append(
            f"🎯 *{comp['titulo']}*\n"
            f"   • Chegada prevista: *{comp['horario_chegada']}*\n"
            f"   • Saindo de: *{opcao['origem_apelido']}* -> {comp['destino']}\n"
            f"   • 🛡️ *Saída segura*: *{opcao['saida_segura']}*{modal_info}\n"
            f"   • Status: {estado['status']}\n"
        )

    return "\n".join(linhas)


def _gerar_orientacao_saida_imediata() -> str:
    """
    Diz qual é o compromisso mais urgente agora e como ir.
    """
    hoje = datetime.now()
    compromissos = listar_compromissos_do_dia(hoje)

    if not compromissos:
        return "Nenhum compromisso pendente para hoje!"

    # Pega o primeiro compromisso ainda não finalizado
    proximo = compromissos[0]
    opcoes = calcular_opcoes_saida_compromisso(proximo)
    opcao = opcoes[0]

    modal_str = ""
    if opcao.get("melhor_modal"):
        modal_str = f"\n💡 *Como ir*: {opcao['melhor_modal']['icone']} {opcao['melhor_modal']['descricao']}"

    return (
        f"🚨 *Próxima Saída:* *{proximo['titulo']}*\n"
        f"📍 De *{opcao['origem_apelido']}* para *{proximo['destino']}*\n"
        f"🎯 Horário de chegada: *{proximo['horario_chegada']}*\n"
        f"🛡️ Saída recomendada: *{opcao['saida_segura']}* (~{opcao['tempo_estimado_min']} min de trajeto)"
        f"{modal_str}"
    )


def _tratar_resposta_origem(numero_escolhido: str) -> str:
    """
    Trata quando o usuário responde '1' ou '2' para a pergunta de onde vai sair.
    """
    hoje = datetime.now()
    compromissos = listar_compromissos_do_dia(hoje)

    # Procura um compromisso que tenha múltiplas origens e esteja pendente
    pendente = None
    for comp in compromissos:
        if comp["perguntar_origem"]:
            pendente = comp
            break

    if not pendente:
        return "⚠️ Não encontrei nenhum compromisso aguardando escolha de origem para hoje."

    resultado = processar_resposta_origem(pendente["id"], numero_escolhido)
    return resultado["mensagem_confirmacao"]


def _tratar_feedback_chegada(texto: str) -> str:
    """
    Trata frases como 'cheguei no horário' ou 'cheguei 10 minutos atrasado'.
    """
    hoje = datetime.now()
    compromissos = listar_compromissos_do_dia(hoje)

    if not compromissos:
        return "Nenhum compromisso ativo encontrado para registrar chegada."

    # Associa o feedback ao compromisso mais recente/ativo
    comp_alvo = compromissos[0]
    resultado = registrar_feedback_chegada(comp_alvo["id"], texto)
    return resultado["mensagem_resposta"]


def _menu_ajuda() -> str:
    return (
        "👋 *Comandos do Vai na Boa:*\n\n"
        "• */status* - Ver resumo de horários e compromissos de hoje\n"
        "• */sair* - Consultar a saída do próximo compromisso\n"
        "• *'1' ou '2'* - Responder de onde você vai sair\n"
        "• *'cheguei no horário'* - Avisar que chegou pontual\n"
        "• *'cheguei X min atrasado'* - Calibrar a margem de segurança"
    )
