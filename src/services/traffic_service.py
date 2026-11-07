from database.traffic_repository import salvar_historico
from services.geocoding_service import obter_coordenadas
from api.multimodal_provider import obter_consenso_transito_vias
from database.location_repository import buscar_local_por_apelido, salvar_local


def obter_local(local):
    registro = buscar_local_por_apelido(local)

    if registro and registro[4] is not None and registro[5] is not None:
        print(f"📌 Local cadastrado encontrado: {registro[1]}")
        return {
            "id": registro[0],
            "nome": registro[1],
            "latitude": registro[4],
            "longitude": registro[5],
        }

    print(f"🌎 Consultando API: {local}")
    coordenadas = obter_coordenadas(local)

    apelido = registro[1] if registro else local
    local_id = salvar_local(
        apelido=apelido,
        endereco_digitado=local,
        endereco_confirmado=coordenadas["endereco"],
        latitude=coordenadas["latitude"],
        longitude=coordenadas["longitude"],
    )

    return {
        "id": local_id,
        "nome": apelido,
        "latitude": coordenadas["latitude"],
        "longitude": coordenadas["longitude"],
    }


def monitorar_rota(origem, destino):
    origem_local = obter_local(origem)
    destino_local = obter_local(destino)

    consenso = obter_consenso_transito_vias(
        origem_local["latitude"],
        origem_local["longitude"],
        destino_local["latitude"],
        destino_local["longitude"],
    )

    salvar_historico(
        origem_local["id"],
        destino_local["id"],
        consenso["distancia_km"],
        consenso["tempo_consolidado_min"],
    )

    return {
        "distancia_km": consenso["distancia_km"],
        "tempo_minutos": consenso["tempo_consolidado_min"],
        "tempo_tomtom_min": consenso["tempo_tomtom_min"],
        "tempo_osrm_min": consenso["tempo_osrm_min"],
        "divergencia_fontes_min": consenso["divergencia_fontes_min"],
    }
