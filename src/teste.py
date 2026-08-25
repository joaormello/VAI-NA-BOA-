from database.favorite_routes_repository import salvar_rota_favorita, listar_rotas_favoritas
from database.init_db import criar_tabela

criar_tabela()
print("TABELAS CRIADAS")


salvar_rota_favorita("casa", "C6")

salvar_rota_favorita("C6", "casa")

for rota in listar_rotas_favoritas():
    print(rota)