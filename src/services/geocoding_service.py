from api.tomtom import buscar_local

def obter_coordenadas(endereco):
    dados = buscar_local(endereco)

    if not dados["results"]:
        raise ValueError(
            f"Endereço não encontrado: {endereco}"
        )

    resultado = dados["results"][0]

    return {
        "endereco": endereco,
        "latitude": resultado["position"]["lat"],
        "longitude": resultado["position"]["lon"]
    }