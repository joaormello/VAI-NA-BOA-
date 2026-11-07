import requests
import urllib3
from config.settings import GOOGLE_MAPS_API_KEY
from services.route_service import obter_resumo_rota

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def consultar_rota_osrm(origem_lat, origem_lon, destino_lat, destino_lon):
    """
    Segunda referência independente de rota viária (OpenStreetMap / OSRM).
    Não exige chave de API e serve para validar/ponderar a estimativa da TomTom.
    """
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origem_lon},{origem_lat};{destino_lon},{destino_lat}"
    )
    params = {"overview": "false", "alternatives": "true"}

    try:
        resp = requests.get(url, params=params, timeout=8, verify=False)
        resp.raise_for_status()
        dados = resp.json()
        if not dados.get("routes"):
            return None

        rota = dados["routes"][0]
        distancia_km = round(rota["distance"] / 1000, 1)
        tempo_min = round(rota["duration"] / 60)
        return {
            "fonte": "OSRM/OpenStreetMap",
            "distancia_km": distancia_km,
            "tempo_minutos": tempo_min,
            "rotas_alternativas_vias": len(dados["routes"]),
        }
    except Exception:
        return None


def consultar_transporte_publico_google(origem_lat, origem_lon, destino_lat, destino_lon):
    """
    Consulta rotas de Transporte Público (SPTrans Ônibus + Metrô/CPTM) via Google Directions API
    quando GOOGLE_MAPS_API_KEY estiver configurada no .env.
    Extrai os números exatos dos ônibus (ex: 746C-10, 8605-10) e linhas de metrô.
    """
    if not GOOGLE_MAPS_API_KEY:
        return []

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origem_lat},{origem_lon}",
        "destination": f"{destino_lat},{destino_lon}",
        "mode": "transit",
        "alternatives": "true",
        "language": "pt-BR",
        "departure_time": "now",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10, verify=False)
        resp.raise_for_status()
        dados = resp.json()
        opcoes = []

        for rota in dados.get("routes", []):
            leg = rota["legs"][0]
            duracao_min = round(leg["duration"]["value"] / 60)
            passos_resumo = []
            modais_usados = set()

            for step in leg.get("steps", []):
                if step.get("travel_mode") == "TRANSIT":
                    detalhes = step.get("transit_details", {})
                    linha = detalhes.get("line", {})
                    veiculo = linha.get("vehicle", {}).get("type", "TRANSIT")
                    nome_curto = linha.get("short_name") or linha.get("name") or "Linha"

                    if veiculo in ("SUBWAY", "HEAVY_RAIL", "COMMUTER_TRAIN"):
                        modais_usados.add("METRO")
                        passos_resumo.append(f"Metrô/Trem {nome_curto}")
                    else:
                        modais_usados.add("ONIBUS")
                        passos_resumo.append(f"Ônibus {nome_curto}")

            if passos_resumo:
                if "METRO" in modais_usados and "ONIBUS" in modais_usados:
                    modal_tipo = "METRO_ONIBUS"
                elif "METRO" in modais_usados:
                    modal_tipo = "METRO"
                else:
                    modal_tipo = "ONIBUS"

                opcoes.append(
                    {
                        "fonte": "Google Transit",
                        "modal": modal_tipo,
                        "descricao_percurso": " + ".join(passos_resumo),
                        "tempo_estimado_min": duracao_min,
                    }
                )

        return opcoes
    except Exception:
        return []


def obter_consenso_transito_vias(origem_lat, origem_lon, destino_lat, destino_lon):
    """
    Consulta múltiplas fontes (TomTom Traffic + OSRM) para não depender cegamente
    de uma única API. Retorna ambas as leituras e o tempo consolidado.
    """
    tomtom = obter_resumo_rota(origem_lat, origem_lon, destino_lat, destino_lon)
    osrm = consultar_rota_osrm(origem_lat, origem_lon, destino_lat, destino_lon)

    tempo_tomtom = tomtom["tempo_minutos"]
    if osrm:
        tempo_osrm = osrm["tempo_minutos"]
        # Pondera 70% TomTom (que tem trânsito em tempo real) + 30% OSRM (referência base)
        # Se TomTom estiver menor que OSRM, usa o maior por segurança contra subestimação
        tempo_consolidado = round(max(tempo_tomtom, (tempo_tomtom * 0.7) + (tempo_osrm * 0.3)))
        divergencia_min = abs(tempo_tomtom - tempo_osrm)
    else:
        tempo_osrm = None
        tempo_consolidado = tempo_tomtom
        divergencia_min = 0

    return {
        "distancia_km": tomtom["distancia_km"],
        "tempo_tomtom_min": tempo_tomtom,
        "tempo_osrm_min": tempo_osrm,
        "tempo_consolidado_min": tempo_consolidado,
        "divergencia_fontes_min": divergencia_min,
    }
