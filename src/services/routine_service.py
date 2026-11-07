from datetime import datetime, timedelta
from analysis.traffic_analysis import (
    calcular_horario_saida,
    calcular_horario_saida_seguro,
    calcular_tempo_rota,
)
from database.appointments_repository import (
    buscar_compromisso_por_id,
    definir_origem_do_dia,
    listar_compromissos_do_dia,
    marcar_pergunta_origem_enviada,
    obter_ou_criar_estado_diario,
    registrar_alerta_enviado,
)
from database.profile_repository import obter_perfil
from services.recomendation_service import recomendar_melhor_modal_e_rota
from services.traffic_service import monitorar_rota


def _minutos_ate_horario(horario_alvo_str, agora=None):
    if agora is None:
        agora = datetime.now()

    alvo_time = datetime.strptime(horario_alvo_str, "%H:%M").time()
    alvo_dt = datetime.combine(agora.date(), alvo_time)
    diferenca_seg = (alvo_dt - agora).total_seconds()
    return round(diferenca_seg / 60)


def calcular_opcoes_saida_compromisso(
    compromisso,
    consultar_tempo_real=False,
    tempo_fallback_min=35,
):
    """
    Calcula o horário de saída seguro para cada origem possível do compromisso
    (ex: Faculdade/IFSP saindo de 'casa' vs saindo do 'C6'), incluindo:
    - Margem de segurança do compromisso
    - Ajuste de aprendizado baseado nos feedbacks reais de atraso pós-chegada
    - Melhor modal/caminho recomendado (Ônibus vs Metrô vs Vias)
    """
    opcoes = []
    chegada_str = compromisso["horario_chegada"]
    destino = compromisso["destino"]
    margem = compromisso.get("margem_seguranca_min", 10)
    ajuste_aprendizado = compromisso.get("ajuste_aprendizado_min", 0) or 0

    for idx, orig in enumerate(compromisso["origens_possiveis"], start=1):
        apelido_origem = orig["apelido"]
        tempo_vias_atual = None

        if consultar_tempo_real:
            try:
                res_live = monitorar_rota(apelido_origem, destino)
                tempo_vias_atual = res_live["tempo_minutos"]
            except Exception:
                pass

        tempo_medio = calcular_tempo_rota(apelido_origem, destino)
        usou_historico = tempo_medio > 0

        if not usou_historico:
            tempo_medio = tempo_vias_atual or tempo_fallback_min

        rec_modal = recomendar_melhor_modal_e_rota(
            apelido_origem,
            destino,
            tempo_vias_atual=tempo_vias_atual or tempo_medio,
        )
        melhor_modal = rec_modal["melhor_opcao"]

        # Se existe um modal específico mais rápido/recomendado (ex: Ônibus ou Metrô), usa o tempo dele como base
        tempo_base_viagem = (
            melhor_modal["tempo_estimado_hoje_min"]
            if melhor_modal
            else tempo_medio
        )

        chegada_dt = datetime.strptime(chegada_str, "%H:%M")
        saida_recomendada = (
            chegada_dt - timedelta(minutes=tempo_base_viagem + ajuste_aprendizado)
        ).strftime("%H:%M")
        saida_segura = (
            chegada_dt - timedelta(minutes=tempo_base_viagem + margem + ajuste_aprendizado)
        ).strftime("%H:%M")

        opcoes.append(
            {
                "opcao_numero": idx,
                "origem_id": orig["id"],
                "origem_apelido": apelido_origem,
                "destino_apelido": destino,
                "tempo_estimado_min": tempo_base_viagem,
                "ajuste_aprendizado_min": ajuste_aprendizado,
                "saida_recomendada": saida_recomendada,
                "saida_segura": saida_segura,
                "usou_historico": usou_historico,
                "melhor_modal": melhor_modal,
                "resumo_modais": rec_modal["resumo_formatado"],
            }
        )

    return opcoes


def gerar_pergunta_origem_whatsapp(compromisso, consultar_tempo_real=False):
    """
    Gera mensagem curta para WhatsApp/Apple Watch perguntando de onde o usuário
    vai sair hoje quando o compromisso aceita múltiplas origens (ex: IFSP).
    """
    opcoes = calcular_opcoes_saida_compromisso(
        compromisso,
        consultar_tempo_real=consultar_tempo_real,
    )
    linhas_opcoes = []
    for op in opcoes:
        dica_modal = (
            f" [{op['melhor_modal']['icone']} {op['melhor_modal']['descricao']}]"
            if op["melhor_modal"]
            else ""
        )
        linhas_opcoes.append(
            f"*{op['opcao_numero']}* - {op['origem_apelido']} "
            f"(saída segura às *{op['saida_segura']}* | ~{op['tempo_estimado_min']} min){dica_modal}"
        )

    texto_opcoes = "\n".join(linhas_opcoes)
    return (
        f"📍 *{compromisso['titulo']}* (Chegada: {compromisso['horario_chegada']})\n"
        f"De onde você vai sair hoje?\n\n"
        f"{texto_opcoes}\n\n"
        f"Responda com o número ou nome do local."
    )


def processar_resposta_origem(appointment_id, resposta_texto, data_str=None):
    """
    Interpreta a resposta do usuário (ex: '1', '2', 'casa', 'C6') e trava a origem
    do compromisso naquele dia para iniciar a contagem regressiva no pulso.
    """
    compromisso = buscar_compromisso_por_id(appointment_id)
    if not compromisso:
        raise ValueError("Compromisso não encontrado.")

    resposta_limpa = str(resposta_texto).strip()
    origens = compromisso["origens_possiveis"]
    origem_escolhida = None

    if resposta_limpa.isdigit():
        indice = int(resposta_limpa) - 1
        if 0 <= indice < len(origens):
            origem_escolhida = origens[indice]["apelido"]
    else:
        for orig in origens:
            if orig["apelido"].lower() == resposta_limpa.lower():
                origem_escolhida = orig["apelido"]
                break

    if not origem_escolhida:
        origem_escolhida = resposta_limpa

    estado = definir_origem_do_dia(appointment_id, origem_escolhida, data_str=data_str)
    opcoes = calcular_opcoes_saida_compromisso(compromisso)
    opcao_ativa = next(
        (o for o in opcoes if o["origem_id"] == estado["origem_escolhida_id"]),
        opcoes[0],
    )

    modal_linha = (
        f"\n{opcao_ativa['melhor_modal']['icone']} Melhor rota: *{opcao_ativa['melhor_modal']['descricao']}*"
        if opcao_ativa["melhor_modal"]
        else ""
    )

    return {
        "estado": estado,
        "mensagem_confirmacao": (
            f"✅ Origem confirmada para *{compromisso['titulo']}*: *{estado['origem_escolhida_apelido']}*\n"
            f"🛡️ Saída segura: *{opcao_ativa['saida_segura']}*{modal_linha}\n"
            f"⌚ Vou te avisar no relógio: 30, 15, 10, 5 min antes e na hora de sair!"
        ),
    }


def formatar_alerta_relogio(
    compromisso,
    origem_apelido,
    horario_saida_segura,
    nivel_alerta_min,
    tempo_rota_min,
    melhor_modal=None,
):
    """
    Formata notificações curtas e diretas pensadas para leitura rápida no Apple Watch:
    30 min -> 15 min -> 10 min -> 5 min -> 0 min (SAIA AGORA).
    """
    titulo = compromisso["titulo"]
    destino = compromisso["destino"]
    chegada = compromisso["horario_chegada"]
    dica_modal = (
        f"\n{melhor_modal['icone']} Vá de: *{melhor_modal['descricao']}*"
        if melhor_modal
        else ""
    )

    if nivel_alerta_min == 0:
        return (
            f"🚨 *SAIA AGORA — {titulo.upper()}!*\n"
            f"🏃 *{origem_apelido}* -> *{destino}* (~{tempo_rota_min} min){dica_modal}\n"
            f"🎯 Chegada prevista até {chegada}. Quando chegar, me avise: *'cheguei no horário'* ou *'cheguei X min atrasado'*!"
        )

    if nivel_alerta_min <= 5:
        icone = "🔥"
        acao = "Pegue suas coisas, quase na hora!"
    elif nivel_alerta_min <= 10:
        icone = "⚠️"
        acao = "Finalize o que está fazendo."
    elif nivel_alerta_min <= 15:
        icone = "⏳"
        acao = "Vá se arrumando para sair."
    else:
        icone = "⌚"
        acao = "Prepare-se com calma."

    return (
        f"{icone} *Faltam {nivel_alerta_min} min para sair ({titulo})*\n"
        f"📍 {origem_apelido} -> {destino}\n"
        f"🛡️ Saída segura às *{horario_saida_segura}* (~{tempo_rota_min} min){dica_modal}\n"
        f"💡 {acao}"
    )


def verificar_eventos_compromisso(
    compromisso,
    agora=None,
    tolerancia_janela_min=2,
    consultar_tempo_real=False,
):
    """
    Verifica se o compromisso precisa disparar agora:
    1) A pergunta de origem (ex: 45 min antes do primeiro horário de saída possível), ou
    2) Algum alerta da escadinha do Apple Watch: 30, 15, 10, 5, 0 (SAIA AGORA).
    """
    if agora is None:
        agora = datetime.now()

    data_str = agora.strftime("%Y-%m-%d")
    perfil = obter_perfil()
    antecedencia_pergunta = perfil["antecedencia_pergunta_origem_min"] if perfil else 45

    estado = obter_ou_criar_estado_diario(compromisso["id"], data_str)
    if estado["status"] in ("SAIU", "CHEGOU", "CANCELADO"):
        return []

    opcoes = calcular_opcoes_saida_compromisso(
        compromisso,
        consultar_tempo_real=consultar_tempo_real,
    )
    eventos_disparados = []

    # 1. Verifica se precisa perguntar de onde o usuário vai sair hoje (ex: IFSP)
    if (
        compromisso["perguntar_origem"]
        and not estado["origem_escolhida_id"]
        and not estado["origem_perguntada"]
    ):
        minutos_menor_saida = min(
            _minutos_ate_horario(op["saida_segura"], agora) for op in opcoes
        )
        if 0 < minutos_menor_saida <= antecedencia_pergunta:
            mensagem = gerar_pergunta_origem_whatsapp(
                compromisso,
                consultar_tempo_real=False,
            )
            marcar_pergunta_origem_enviada(compromisso["id"], data_str)
            eventos_disparados.append(
                {
                    "tipo": "PERGUNTA_ORIGEM",
                    "appointment_id": compromisso["id"],
                    "mensagem": mensagem,
                }
            )
            return eventos_disparados

    # 2. Define qual origem usar para a contagem regressiva (escolhida hoje ou padrão)
    origem_ativa_id = estado["origem_escolhida_id"] or compromisso["origem_id"]
    opcao_ativa = next(
        (o for o in opcoes if o["origem_id"] == origem_ativa_id),
        opcoes[0],
    )

    horario_saida = opcao_ativa["saida_segura"]
    minutos_restantes = _minutos_ate_horario(horario_saida, agora)

    # 3. Avalia a escadinha de alertas (30, 15, 10, 5, 0 min)
    for nivel in compromisso["alertas_minutos_lista"]:
        if nivel in estado["alertas_enviados"]:
            continue

        if (nivel - tolerancia_janela_min) <= minutos_restantes <= nivel:
            msg = formatar_alerta_relogio(
                compromisso=compromisso,
                origem_apelido=opcao_ativa["origem_apelido"],
                horario_saida_segura=horario_saida,
                nivel_alerta_min=nivel,
                tempo_rota_min=opcao_ativa["tempo_estimado_min"],
                melhor_modal=opcao_ativa["melhor_modal"],
            )
            registrar_alerta_enviado(
                appointment_id=compromisso["id"],
                minutos_antes=nivel,
                horario_saida_calculado=horario_saida,
                data_str=data_str,
            )
            eventos_disparados.append(
                {
                    "tipo": "ALERTA_RELOGIO",
                    "nivel_minutos": nivel,
                    "appointment_id": compromisso["id"],
                    "horario_saida": horario_saida,
                    "mensagem": msg,
                }
            )
            break

    return eventos_disparados
