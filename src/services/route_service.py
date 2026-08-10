from api.routing import calcular_rota

def obter_resumo_rota(
        origem_lat, 
        origem_lon, 
        destino_lat,
        destino_lon
):
    dados = calcular_rota(
        origem_lat,
        origem_lon,
        destino_lat, 
        destino_lon
    )

    rota = dados["routes"][0]
    resumo = rota["summary"]
    distancia_km = (
        resumo["lengthInMeters"]/1000
    )

    tempo_minutos = (
        resumo["travelTimeInSeconds"]/60
    )

    return {"distancia_km" : round(distancia_km, 1), "tempo_minutos": round(tempo_minutos)}
