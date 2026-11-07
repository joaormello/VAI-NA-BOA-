import requests
from config.settings import TOMTOM_API_KEY
import urllib3

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

def buscar_local(endereco):
    url = f"https://api.tomtom.com/search/2/search/{endereco}.json"

    parametros = {
        "key": TOMTOM_API_KEY,
        "limit": 1
    }

    resposta = requests.get(url, params=parametros, timeout=8, verify=False)
    resposta.raise_for_status()
    return resposta.json()
