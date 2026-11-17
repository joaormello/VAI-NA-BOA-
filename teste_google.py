import requests

api_key = "AIzaSyB09QrmQVrwVGKUEFPuZEcF2raUm4wkhgs"

# Teste: Casa (Dr. Luiz Migliano) -> C6 (Av. Nove de Julho, 3186)
url = "https://maps.googleapis.com/maps/api/directions/json"
params = {
    "origin": "-23.622323,-46.739611",
    "destination": "-23.5674888,-46.659757",
    "mode": "transit",
    "alternatives": "true",
    "language": "pt-BR",
    "key": api_key,
}

resp = requests.get(url, params=params, timeout=12)
dados = resp.json()

print("Status HTTP:", resp.status_code)
print("Status Google:", dados.get("status"))

if dados.get("status") == "OK":
    rotas = dados.get("routes", [])
    print(f"Total de rotas de transporte publico encontradas: {len(rotas)}\n")
    for i, r in enumerate(rotas, 1):
        leg = r["legs"][0]
        duracao = leg["duration"]["text"]
        passos = []
        for s in leg.get("steps", []):
            if s.get("travel_mode") == "TRANSIT":
                linha = s.get("transit_details", {}).get("line", {})
                tipo = linha.get("vehicle", {}).get("type", "TRANSIT")
                nome = linha.get("short_name") or linha.get("name")
                passos.append(f"{tipo} {nome}")
            elif s.get("travel_mode") == "WALKING":
                passos.append(f"Caminhada ({s['duration']['text']})")
        print(f"Opcao {i} (~{duracao}):")
        print(" -> ".join(passos))
        print("-" * 50)
else:
    print("Erro detalhado:", dados.get("error_message"))
