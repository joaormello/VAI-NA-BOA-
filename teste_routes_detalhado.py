import requests

api_key = "AIzaSyB09QrmQVrwVGKUEFPuZEcF2raUm4wkhgs"

url = "https://routes.googleapis.com/directions/v2:computeRoutes"
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.transitDetails,routes.legs.steps.travelMode",
}

payload = {
    "origin": {
        "location": {
            "latLng": {"latitude": -23.622323, "longitude": -46.739611}
        }
    },
    "destination": {
        "location": {
            "latLng": {"latitude": -23.5674888, "longitude": -46.659757}
        }
    },
    "travelMode": "TRANSIT",
    "computeAlternativeRoutes": True,
    "languageCode": "pt-BR",
}

resp = requests.post(url, json=payload, headers=headers, timeout=12)
dados = resp.json()

print(f"Status HTTP: {resp.status_code}")
rotas = dados.get("routes", [])
print(f"Total de alternativas de transporte publico encontradas: {len(rotas)}\n")

for i, r in enumerate(rotas, 1):
    duracao_seg = int(r.get("duration", "0s").replace("s", ""))
    duracao_min = round(duracao_seg / 60)
    
    etapas = []
    for leg in r.get("legs", []):
        for s in leg.get("steps", []):
            mode = s.get("travelMode")
            if mode == "TRANSIT":
                det = s.get("transitDetails", {})
                linha = det.get("transitLine", {})
                num = linha.get("nameShort") or linha.get("name")
                veiculo = linha.get("vehicle", {}).get("type", "TRANSIT")
                etapas.append(f"{veiculo} {num}")
            elif mode == "WALK":
                etapas.append("Caminhada")
                
    print(f"Opcao {i}: ~{duracao_min} minutos")
    print(" -> ".join(etapas))
    print("-" * 50)
