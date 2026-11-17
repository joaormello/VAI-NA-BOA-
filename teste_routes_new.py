import requests

api_key = "AIzaSyB09QrmQVrwVGKUEFPuZEcF2raUm4wkhgs"

# Chamada na nova Google Routes API (Next-Gen) com suporte a TRANSIT
url = "https://routes.googleapis.com/directions/v2:computeRoutes"
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.transitDetails,routes.legs.steps.navigationInstruction",
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
print("Status Google Routes API (New):", resp.status_code)
print("Resposta:\n", resp.text[:400])
