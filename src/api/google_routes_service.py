import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


def consultar_rotas_transporte_google(origem_lat, origem_lon, destino_lat, destino_lon):
    """
    Consulta alternativas em tempo real de transporte publico (Onibus SPTrans + Metro)
    atraves da Google Routes API (Next-Gen).
    """
    if not GOOGLE_MAPS_API_KEY:
        return []

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.transitDetails,routes.legs.steps.travelMode",
    }

    payload = {
        "origin": {
            "location": {"latLng": {"latitude": origem_lat, "longitude": origem_lon}}
        },
        "destination": {
            "location": {"latLng": {"latitude": destino_lat, "longitude": destino_lon}}
        },
        "travelMode": "TRANSIT",
        "computeAlternativeRoutes": True,
        "languageCode": "pt-BR",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        dados = resp.json()
        rotas = dados.get("routes", [])

        opcoes = []
        for r in rotas:
            duracao_seg = int(r.get("duration", "0s").replace("s", ""))
            duracao_min = round(duracao_seg / 60)

            etapas_formatadas = []
            modais = set()

            for leg in r.get("legs", []):
                for s in leg.get("steps", []):
                    mode = s.get("travelMode")
                    if mode == "TRANSIT":
                        det = s.get("transitDetails", {})
                        linha = det.get("transitLine", {})
                        nome = linha.get("nameShort") or linha.get("name")
                        tipo = linha.get("vehicle", {}).get("type", "TRANSIT")

                        if tipo in ("SUBWAY", "METRO", "HEAVY_RAIL"):
                            modais.add("METRO")
                            etapas_formatadas.append(f"Metrô {nome}")
                        else:
                            modais.add("ONIBUS")
                            etapas_formatadas.append(f"Ônibus {nome}")

            if etapas_formatadas:
                if "METRO" in modais and "ONIBUS" in modais:
                    modal_tipo = "METRO_ONIBUS"
                elif "METRO" in modais:
                    modal_tipo = "METRO"
                else:
                    modal_tipo = "ONIBUS"

                opcoes.append(
                    {
                        "fonte": "Google Routes (Live)",
                        "modal": modal_tipo,
                        "descricao_percurso": " + ".join(etapas_formatadas),
                        "tempo_estimado_min": duracao_min,
                    }
                )

        return opcoes
    except Exception as err:
        print(f"[Aviso] Erro ao consultar Google Routes: {err}")
        return []
