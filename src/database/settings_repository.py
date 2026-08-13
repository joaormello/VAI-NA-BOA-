from database.sqlite_db import get_connetcion

def salvar_configuracao(
        origem, 
        destino,
        horario_chegada
):
    conn = get_connetcion
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO settings(
            origem, 
            destino,
            horario_chegada
        )
        VALUES (?, ?,?)
    """,
    (
        origem,
        destino,
        horario_chegada
    ))
    conn.commit()
    conn.close()

    