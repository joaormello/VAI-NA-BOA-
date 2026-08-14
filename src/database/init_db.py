from database.sqlite_db import get_connetcion

def criar_tabela():
    conn = get_connetcion()
    cursor = conn.cursor()

    #tabela de locais
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



    #tabela de histórico de trânsito
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        data_hora TEXT,
        origem TEXT,
        destino TEXT,
        distancia_km REAL,
        tempo_minutos INTEGER 
        )
""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origem TEXT,
        destino TEXT, 
        horario_chegada TEXT
        )
    """)
    conn.commit()
    conn.close()


