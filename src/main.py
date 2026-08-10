from services.geocoding_service import (obter_coordenadas)
from services.route_service import (obter_resumo_rota)


origem_endereco = "Portal do Morumbi, São Paulo"
destino_endereco = "Estação Morumbi Claro, São Paulo"

origem = obter_coordenadas(origem_endereco)
destino = obter_coordenadas(destino_endereco)

rota = obter_resumo_rota(
    origem["latitude"],
    origem["longitude"],
    destino["latitude"],
    destino["longitude"]
)

print("=" * 40)
print("🚗 VAI NA BOA")
print("=" * 40)

print()

print(
    f"📍 Origem: {origem_endereco}"
)

print(
    f"📍 Destino: {destino_endereco}"
)

print()

print(
    f"📏 Distância: "
    f"{rota['distancia_km']} km"
)

print(
    f"⏱️ Tempo estimado: "
    f"{rota['tempo_minutos']} min"
)