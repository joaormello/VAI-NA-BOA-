from database.init_db import criar_tabela
from database.location_repository import salvar_local
from database.location_repository import listar_locais

criar_tabela()

salvar_local(
    "casa",
    "Luiz Migliano, 1870",
    "Dr. Luiz Migliano, 1870 - Jd Caboré, São Paulo",
    -23.62,
    -46.72

)

locais = listar_locais()
print("Local Salvo.")
print(locais)