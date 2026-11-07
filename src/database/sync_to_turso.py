"""
src/database/sync_to_turso.py
Sincroniza o schema e os dados reais locais do SQLite para o Turso na nuvem.
"""
import sys
import sqlite3
from pathlib import Path

BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from database.sqlite_db import DATABASE_PATH, get_connection

TABELAS = [
    "schema_migrations",
    "locations",
    "settings",
    "favorite_routes",
    "traffic_history",
    "user_profile",
    "appointments",
    "appointment_daily_state",
    "route_alternatives",
]


def migrar():
    print("Iniciando sincronizacao do SQLite local para o Turso na nuvem...")
    local_conn = sqlite3.connect(DATABASE_PATH)
    turso_conn = get_connection()

    # 1. Pega os DDLs de criacao de tabelas do SQLite local
    cursor_local = local_conn.cursor()
    cursor_local.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tabelas_locais = cursor_local.fetchall()

    for nome, ddl in tabelas_locais:
        print(f"Criando tabela no Turso: {nome}...")
        turso_conn.execute(ddl)

    # 2. Copia os dados linha por linha
    for tab in TABELAS:
        try:
            cursor_local.execute(f"SELECT * FROM {tab};")
            linhas = cursor_local.fetchall()
            if not linhas:
                continue

            colunas = [d[0] for d in cursor_local.description]
            placeholders = ", ".join(["?"] * len(colunas))
            cols_str = ", ".join(colunas)
            sql_insert = f"INSERT OR REPLACE INTO {tab} ({cols_str}) VALUES ({placeholders});"

            print(f"Copiando {len(linhas)} registros da tabela {tab}...")
            for l in linhas:
                turso_conn.execute(sql_insert, l)

        except Exception as err:
            print(f"Nota para tabela {tab}: {err}")

    local_conn.close()
    print("Sincronizacao com o Turso finalizada com sucesso!")


if __name__ == "__main__":
    migrar()
