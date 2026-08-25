from services.traffic_service import monitorar_rota

def executar_coleta(origem, destino):
    monitorar_rota(origem, destino)

    return(
        f"Coleta realizada: "
        f"{origem} -> {destino}"
    )