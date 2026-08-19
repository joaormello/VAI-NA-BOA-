from database.traffic_repository import listar_historico

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
        1
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

    diferenca = (
        (tempo_atual- media)/ media
    ) * 100

    if diferenca > 0 :
        return (
            f"⚠️ Trânsito "
            f"{round(diferenca, 1)}% "
            f"acima da média."
        )

    elif diferenca < 0 : 
        return (
            f"✅ Trânsito "
            f"{abs(round(diferenca, 1))}% "
            f"abaixo da média."
        )

    return "Trânsito denstro da média"




def media_por_hora():
    historico = listar_historico()

    horas = {}

    for registro in historico:
        data_hora = registro[1]
        hora = data_hora [11:13]
        tempo = registro[5]

        if hora not in horas:
            horas[hora] = []

        horas[hora].append(tempo)

    medias = {}

    for hora in horas:
        media = (
            sum(horas[hora])/len(horas[hora])
        )

        medias[hora] = round(media, 1)

    return medias



def melhor_horario():
    medias = media_por_hora()

    if not medias : 
        return None

    melhor = min(
        medias, 
        key = medias.get
    )

    return melhor   


def pior_horario():

    medias = media_por_hora()

    if not medias : 
        return None 

    pior = max(
        medias, 
        key = medias.get
    )

    return pior