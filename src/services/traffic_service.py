from database.traffic_repository import salvar_historico
from services.geocoding_service import obter_coordenadas
from services.route_service import obter_resumo_rota

def monitorar_rota(
        origem_endereco,
        destino_endereco
):
    origem = obter_coordenadas(origem_endereco)
    destino = obter_coordenadas(destino_endereco)

    rota = obter_resumo_rota(
        origem["latitude"],
        origem["longitude"],
        destino["latitude"],
        destino["longitude"]
    )

    salvar_historico(
        origem_endereco,
        destino_endereco,
        rota["distancia_km"],
        rota["tempo_minutos"]
    )

    return rota