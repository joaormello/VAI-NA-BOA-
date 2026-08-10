import requests
from config.settings import TOMTOM_API_KEY

def buscar_local(endereco):
    url = f"https://api.tomtom.com/search/2/search/{endereco}.json"

    parametros = {
        "key": TOMTOM_API_KEY,
        "limit":1
    }

    resposta = requests.get(url, params=parametros)
    resposta.raise_for_status()
    return resposta.json()
