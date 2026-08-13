from database.init_db import criar_tabela
from database.location_repository import salvar_local
from database.location_repository import (listar_locais, buscar_local_por_apelido, atualizar_local,excluir_local)

criar_tabela()

salvar_local(
    "casa",
    "Luiz Migliano, 1870",
    "Dr. Luiz Migliano, 1870 - Jd Caboré, São Paulo",
    -23.62,
    -46.72

)

atualizar_local(
    "casa",
    "Rua Nova, 130",
    -23.50,
    -46.60
)

local = buscar_local_por_apelido("casa")

print(local)


excluir_local("casa")

print(listar_locais())
