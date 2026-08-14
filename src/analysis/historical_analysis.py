from database.traffic_repository import (listar_historico)


def calcular_tempo_medio():
    historico = listar_historico()

    if not historico:
        return 0 

    soma = 0 

    for registro in historico:
        tempo_minutos = registro[5]
        soma += tempo_minutos

    return round(
        soma/len(historico),
        1
    )


def maior_tempo():
    historico = listar_historico()

    if not historico:
        return 0 

    maior = 0

    for registro in historico:

        tempo = registro[5]

        if tempo > maior:
            maior = tempo

    return maior


def menor_tempo():
    historico = listar_historico()

    if not historico:
        return 0 

    menor = historico[0][5]
    for registro in historico: 
        tempo = registro[5]

        if tempo < menor :
            menor = tempo

    return menor    