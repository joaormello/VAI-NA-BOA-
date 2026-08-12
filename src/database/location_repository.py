from database.sqlite_db import get_connetcion

def salvar_local(
        apelido,
        endereco_digitado, 
        endereco_confirmado,
        latitude,
        longitude,
):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO locations (
            apelido,
            endereco_digitado,
            endereco_confirmado,
            latitude,
            longitude   
        )
        VALUES (?, ?, ?, ?, ?)
  """,
    (
        apelido, 
        endereco_digitado,
        endereco_confirmado,
        latitude,
        longitude
    ))

    conn.commit()
    conn.close()


def listar_locais():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM locations
   """ )

    locais = cursor.fetchall()
    conn.close()

    return locais