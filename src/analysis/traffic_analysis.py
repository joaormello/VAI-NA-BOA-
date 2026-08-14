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