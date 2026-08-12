from database.sqlite_db import get_connetcion

def criar_tabela():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apelido TEXT NOT NULL,
            endereco_digitado TEXT,
            endereco_confirmado TEXT,
            latitude REAL,
            longitude REAL
        )
  """ )

    conn.commit()
    conn.close()