from database.traffic_repository import salvar_historico
from services.geocoding_service import obter_coordenadas
from services.route_service import obter_resumo_rota
from database.location_repository import buscar_local_por_apelido

def obter_local(local):
    registro = buscar_local_por_apelido(local)

    if registro:
        print(
            f"📌 Local cadastrado encontrado: {local}"
        )

        return{
            "nome": registro[1],
            "latitude": registro[4],
            "longitude": registro[5]
        }
    print(
        f"🌎 Consultando API: {local}"
    )

    return obter_coordenadas(local)


def monitorar_rota(
        origem,
        destino
):
    origem_local = obter_local(origem)
    destino_local = obter_local(destino)

    print(origem_local)
    print(destino_local)
    rota = obter_resumo_rota(
        origem_local["latitude"],
        origem_local["longitude"],
        destino_local["latitude"],
        destino_local["longitude"]
    )

    salvar_historico(
        origem,
        destino,
        rota["distancia_km"],
        rota["tempo_minutos"]
    )

    return rota