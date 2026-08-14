from database.sqlite_db import get_connetcion
from datetime import datetime


def salvar_historico(
        origem, 
        destino,
        distancia_km,
        tempo_minutos
):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO traffic_history(
            data_hora,
            origem,
            destino,
            distancia_km,
            tempo_minutos
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        data_hora,
        origem,
        destino,
        distancia_km,
        tempo_minutos
    ))

    conn.commit()
    conn.close()


def listar_historico():

    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM traffic_history
    """)

    historico = cursor.fetchall()
    conn.close()
    return historico