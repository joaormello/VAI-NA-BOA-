from pipeline.collect_pipline import executar_coleta
from database.favorite_routes_repository import listar_rotas_favoritas

rotas = listar_rotas_favoritas()


print(
    f"Coletando {len(rotas)} rotas..."
)

for rota in rotas:
    origem = rota[1]
    destino = rota[2]

    print(
        executar_coleta(origem, destino)
    )

print("✅ Coleta finalizada.")