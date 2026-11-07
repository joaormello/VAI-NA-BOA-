from database.traffic_repository import listar_historico, listar_historico_rota
from datetime import datetime, timedelta


def contar_registros():
    historico = listar_historico()
    return len(historico)


def calcular_tempo():
    historico = listar_historico()

    if not historico:
        return 0
    soma = 0

    for registro in historico:
        soma += registro[5]

    return round(
        soma / len(historico),
        1,
    )


def obter_melhor_tempo():
    historico = listar_historico()

    if not historico:
        return 0

    tempos = []

    for registro in historico:
        tempos.append(registro[5])

    return min(tempos)


def obter_pior_tempo():
    historico = listar_historico()

    if not historico:
        return 0

    tempos = []

    for registro in historico:
        tempos.append(registro[5])

    return max(tempos)


def comparar_com_media(tempo_atual):
    media = calcular_tempo()

    if media == 0:
        return "Sem histórico suficiente"

    diferenca = ((tempo_atual - media) / media) * 100

    if diferenca > 0:
        return (
            f"⚠️ Trânsito "
            f"{round(diferenca, 1)}% "
            f"acima da média."
        )

    elif diferenca < 0:
        return (
            f"✅ Trânsito "
            f"{abs(round(diferenca, 1))}% "
            f"abaixo da média."
        )

    return "Trânsito dentro da média"


def media_por_hora():
    historico = listar_historico()

    horas = {}

    for registro in historico:
        data_hora = registro[1]
        hora = data_hora[11:13]
        tempo = registro[5]

        if hora not in horas:
            horas[hora] = []

        horas[hora].append(tempo)

    medias = {}

    for hora in horas:
        media = sum(horas[hora]) / len(horas[hora])
        medias[hora] = round(media, 1)

    return medias


def melhor_horario():
    medias = media_por_hora()

    if not medias:
        return None

    melhor = min(
        medias,
        key=medias.get,
    )

    return melhor


def pior_horario():
    medias = media_por_hora()

    if not medias:
        return None

    pior = max(
        medias,
        key=medias.get,
    )

    return pior


def calcular_tempo_rota(origem, destino):
    historico = listar_historico_rota(origem, destino)

    if not historico:
        return 0

    soma = 0

    for registro in historico:
        soma += registro[5]

    return round(soma / len(historico), 1)


def melhor_tempo_rota(origem, destino):
    historico = listar_historico_rota(origem, destino)

    if not historico:
        return 0

    tempos = []

    for registro in historico:
        tempos.append(registro[5])

    return min(tempos)


def pior_tempo_rota(origem, destino):
    historico = listar_historico_rota(origem, destino)

    if not historico:
        return 0

    tempos = []
    for registro in historico:
        tempos.append(registro[5])

    return max(tempos)


def total_consultas_rota(origem, destino):
    historico = listar_historico_rota(origem, destino)
    return len(historico)


def melhor_horario_rota(origem, destino):
    medias = media_por_hora_rota(origem, destino)

    if not medias:
        return None

    return min(medias, key=medias.get)


def pior_horario_rota(origem, destino):
    medias = media_por_hora_rota(origem, destino)

    if not medias:
        return None

    return max(medias, key=medias.get)


def media_por_hora_rota(origem, destino):
    historico = listar_historico_rota(origem, destino)

    horas = {}

    for registro in historico:
        data_hora = registro[1]
        hora = data_hora[11:13]
        tempo = registro[5]

        if hora not in horas:
            horas[hora] = []
        horas[hora].append(tempo)

    medias = {}

    for hora in horas:
        media = sum(horas[hora]) / len(horas[hora])
        medias[hora] = round(media, 1)

    return medias


def comparar_com_media_rota(origem, destino, tempo_atual):
    media = calcular_tempo_rota(origem, destino)

    if media == 0:
        return "Sem histórico suficiente"

    diferenca = ((tempo_atual - media) / media) * 100

    if diferenca > 0:
        return (
            f"⚠️ Trânsito "
            f"{round(diferenca, 1)}% "
            f"acima da média."
        )

    elif diferenca < 0:
        return (
            f"✅ Trânsito "
            f"{abs(round(diferenca, 1))}% "
            f"abaixo da média."
        )

    return "Trânsito dentro da média"


def calcular_horario_saida(
    origem,
    destino,
    horario_chegada,
    ajuste_extra_min=0,
):
    tempo_medio = calcular_tempo_rota(origem, destino)

    if tempo_medio == 0:
        return None

    chegada = datetime.strptime(horario_chegada, "%H:%M")
    saida = chegada - timedelta(minutes=tempo_medio + ajuste_extra_min)

    return saida.strftime("%H:%M")


def calcular_horario_saida_seguro(
    origem,
    destino,
    horario_chegada,
    margem=10,
    ajuste_extra_min=0,
):
    tempo_medio = calcular_tempo_rota(origem, destino)

    if tempo_medio == 0:
        return None

    chegada = datetime.strptime(horario_chegada, "%H:%M")
    saida = chegada - timedelta(minutes=tempo_medio + margem + ajuste_extra_min)

    return saida.strftime("%H:%M")


# =====================================================================
# FASE 11: RISCO DE ATRASO ESTATÍSTICO
# =====================================================================
def calcular_risco_atraso(
    origem,
    destino,
    horario_chegada=None,
    tempo_atual=None,
    margem_extra_min=0,
    agora=None,
):
    """
    Calcula o nível de risco de atraso ('BAIXO', 'MEDIO', 'ALTO', 'CRITICO')
    cruzando:
    1) A variação do tempo atual em relação à média histórica e ao pior tempo;
    2) O tempo restante até o horário de chegada (se informado).
    """
    media = calcular_tempo_rota(origem, destino)
    pior = pior_tempo_rota(origem, destino)
    tempo_ref = (tempo_atual if tempo_atual is not None else media) + margem_extra_min

    if media == 0 and tempo_atual is None:
        return {
            "nivel": "INDEFINIDO",
            "probabilidade_pct": 0,
            "icone": "⚪",
            "mensagem": "Sem histórico suficiente para calcular risco de atraso.",
        }

    variacao_pct = ((tempo_ref - media) / media * 100) if media > 0 else 0

    folga_minutos = None
    if horario_chegada:
        if agora is None:
            agora = datetime.now()
        alvo_time = datetime.strptime(horario_chegada, "%H:%M").time()
        alvo_dt = datetime.combine(agora.date(), alvo_time)
        minutos_disponiveis = (alvo_dt - agora).total_seconds() / 60
        folga_minutos = round(minutos_disponiveis - tempo_ref)

    if folga_minutos is not None and folga_minutos < 0:
        return {
            "nivel": "CRITICO",
            "probabilidade_pct": 95,
            "icone": "🚨",
            "folga_minutos": folga_minutos,
            "mensagem": (
                f"🚨 Risco CRÍTICO de atraso (~{abs(folga_minutos)} min atrasado se sair agora)."
            ),
        }

    if (folga_minutos is not None and folga_minutos <= 5) or variacao_pct >= 25 or (pior > 0 and tempo_ref >= pior):
        return {
            "nivel": "ALTO",
            "probabilidade_pct": 75,
            "icone": "🔴",
            "folga_minutos": folga_minutos,
            "mensagem": "🔴 Risco ALTO de atraso: trânsito pesado ou margem no limite.",
        }

    if (folga_minutos is not None and folga_minutos <= 12) or variacao_pct >= 10:
        return {
            "nivel": "MEDIO",
            "probabilidade_pct": 40,
            "icone": "🟡",
            "folga_minutos": folga_minutos,
            "mensagem": "🟡 Risco MÉDIO de atraso: atenção ao horário de saída.",
        }

    return {
        "nivel": "BAIXO",
        "probabilidade_pct": 10,
        "icone": "🟢",
        "folga_minutos": folga_minutos,
        "mensagem": "🟢 Risco BAIXO de atraso: condições favoráveis.",
    }


# =====================================================================
# FASE 12: PREVISÃO DE PIORA NO TRÂNSITO POR FAIXA DE HORÁRIO
# =====================================================================
def prever_piora_transito(origem, destino):
    """
    Analisa a curva histórica por hora da rota para identificar saltos de congestionamento
    (ex: 'Após as 14:00 o trânsito aumenta 21% nessa rota').
    """
    medias = media_por_hora_rota(origem, destino)
    if len(medias) < 2:
        return "📊 Coletando mais horários diferentes para prever janelas de pico."

    horas_ordenadas = sorted(medias.keys())
    maior_salto_pct = 0
    hora_antes = None
    hora_pico = None

    for i in range(len(horas_ordenadas) - 1):
        h1 = horas_ordenadas[i]
        h2 = horas_ordenadas[i + 1]
        t1 = medias[h1]
        t2 = medias[h2]
        if t1 > 0:
            aumento_pct = ((t2 - t1) / t1) * 100
            if aumento_pct > maior_salto_pct:
                maior_salto_pct = aumento_pct
                hora_antes = h1
                hora_pico = h2

    if maior_salto_pct >= 10 and hora_pico is not None:
        return (
            f"📈 Previsão de trânsito: Entre {hora_antes}:00 e {hora_pico}:00 "
            f"o tempo de viagem costuma subir {round(maior_salto_pct)}% "
            f"(de ~{medias[hora_antes]} min para ~{medias[hora_pico]} min)."
        )

    pior_h = max(medias, key=medias.get)
    melhor_h = min(medias, key=medias.get)
    if pior_h != melhor_h:
        diff_pct = round(((medias[pior_h] - medias[melhor_h]) / medias[melhor_h]) * 100)
        return (
            f"📊 Janela de atenção: O horário das {pior_h}:00 costuma ser {diff_pct}% "
            f"mais lento (~{medias[pior_h]} min) que às {melhor_h}:00 (~{medias[melhor_h]} min)."
        )

    return "✅ Trânsito historicamente estável entre as faixas horárias registradas."
