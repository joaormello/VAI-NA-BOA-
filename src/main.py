from services.traffic_service import monitorar_rota
from database.traffic_repository import listar_historico

rota = monitorar_rota(
    "Portal do Morumbi, São Paulo",
    "Enem Morumbi, São Paulo"
)

print()
print("HISTORICO")
print(listar_historico())