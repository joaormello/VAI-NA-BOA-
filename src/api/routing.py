import requests 
from config.settings import TOMTOM_API_KEY

def calcular_rota(
        origem_lat, 
        origem_lon,
        destino_lat,
        destino_lon
):
    url = (
        "https://api.tomtom.com/routing/1/"
        f"calculateRoute/"
        f"{origem_lat},{origem_lon}:"
        f"{destino_lat},{destino_lon}/json"
    )

    params = {
        "key": TOMTOM_API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()