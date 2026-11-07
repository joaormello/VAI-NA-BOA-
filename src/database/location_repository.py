from database.sqlite_db import get_connetcion


def salvar_local(
    apelido,
    endereco_digitado,
    endereco_confirmado,
    latitude,
    longitude,
):
    existente = buscar_local_por_apelido(apelido)
    if existente:
        atualizar_local(
            existente[1],
            endereco_confirmado,
            latitude,
            longitude,
        )
        return existente[0]

    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
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
            longitude,
        ),
    )

    local_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return local_id


def listar_locais():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM locations
    """)

    locais = cursor.fetchall()
    conn.close()

    return locais


def buscar_local_por_id(local_id):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM locations
        WHERE id = ?
        """,
        (local_id,),
    )

    local = cursor.fetchone()
    conn.close()
    return local


def buscar_local_por_apelido(apelido):
    conn = get_connetcion()
    cursor = conn.cursor()

    # 1. Busca exata pelo apelido (case-insensitive)
    cursor.execute(
        """
        SELECT *
        FROM locations
        WHERE apelido = ? COLLATE NOCASE
        """,
        (apelido,),
    )
    local = cursor.fetchone()

    # 2. Caso o usuário passe o endereço em vez do apelido, verifica endereços cadastrados
    if not local:
        cursor.execute(
            """
            SELECT *
            FROM locations
            WHERE endereco_digitado = ? COLLATE NOCASE
               OR endereco_confirmado = ? COLLATE NOCASE
               OR endereco_confirmado LIKE ?
            """,
            (apelido, apelido, f"%{apelido}%"),
        )
        local = cursor.fetchone()

    conn.close()
    return local


def resolver_local_id(identificador, criar_se_nao_existir=False):
    if isinstance(identificador, int):
        return identificador

    local = buscar_local_por_apelido(identificador)
    if local:
        return local[0]

    if criar_se_nao_existir:
        return salvar_local(
            apelido=identificador,
            endereco_digitado=identificador,
            endereco_confirmado=identificador,
            latitude=None,
            longitude=None,
        )

    return None


def atualizar_local(
    apelido,
    endereco_confirmado,
    latitude,
    longitude,
):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE locations
        SET endereco_confirmado = ?,
            latitude = ?,
            longitude = ?
        WHERE apelido = ? COLLATE NOCASE
        """,
        (
            endereco_confirmado,
            latitude,
            longitude,
            apelido,
        ),
    )
    conn.commit()
    conn.close()


def excluir_local(apelido):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM locations
        WHERE apelido = ? COLLATE NOCASE
        """,
        (apelido,),
    )

    conn.commit()
    conn.close()
