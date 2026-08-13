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



def buscar_local_por_apelido(apelido):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM locations
        WHERE apelido = ?
""", (apelido,))

    local = cursor.fetchone()
    conn.close()
    return local

def atualizar_local(
        apelido,
        endereco_confirmado,
        latitude,
        longitude
):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE locations
        SET endereco_confirmado = ?,
            latitude = ?,
            longitude = ?
        WHERE apelido = ?
""",
(
    endereco_confirmado,
    latitude,
    longitude,
    apelido

))
    conn.commit()
    conn.close()


def excluir_local(apelido):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM locations
        WHERE apelido = ?
""", (apelido,))

    conn.commit()
    conn.close()