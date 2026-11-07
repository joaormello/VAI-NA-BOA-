from database.sqlite_db import get_connection
from database.location_repository import resolver_local_id


def cadastrar_alternativa_rota(
    origem,
    destino,
    modal,
    descricao_percurso,
    tempo_base_min,
    sensibilidade_transito=1.0,
    preferencial=False,
):
    """
    Cadastra uma opção real de caminho/modal para uma rota (ex: Ônibus 746C-10 + 8605,
    Metrô Linha 4-Amarela, ou Carro/Uber) para o sistema comparar e recomendar o melhor modal.
    """
    origem_id = resolver_local_id(origem, criar_se_nao_existir=True)
    destino_id = resolver_local_id(destino, criar_se_nao_existir=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM route_alternatives
        WHERE origem_id = ? AND destino_id = ? AND descricao_percurso = ? COLLATE NOCASE
        """,
        (origem_id, destino_id, descricao_percurso),
    )
    existente = cursor.fetchone()
    if existente:
        cursor.execute(
            """
            UPDATE route_alternatives
            SET modal = ?,
                tempo_base_min = ?,
                sensibilidade_transito = ?,
                preferencial = ?,
                ativo = 1
            WHERE id = ?
            """,
            (
                modal.upper(),
                tempo_base_min,
                sensibilidade_transito,
                1 if preferencial else 0,
                existente[0],
            ),
        )
        alt_id = existente[0]
    else:
        cursor.execute(
            """
            INSERT INTO route_alternatives (
                origem_id,
                destino_id,
                modal,
                descricao_percurso,
                tempo_base_min,
                sensibilidade_transito,
                preferencial,
                ativo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                origem_id,
                destino_id,
                modal.upper(),
                descricao_percurso,
                tempo_base_min,
                sensibilidade_transito,
                1 if preferencial else 0,
            ),
        )
        alt_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return alt_id


def listar_alternativas_rota(origem, destino):
    origem_id = resolver_local_id(origem, criar_se_nao_existir=False)
    destino_id = resolver_local_id(destino, criar_se_nao_existir=False)

    if origem_id is None or destino_id is None:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            origem_id,
            destino_id,
            modal,
            descricao_percurso,
            tempo_base_min,
            sensibilidade_transito,
            preferencial
        FROM route_alternatives
        WHERE origem_id = ? AND destino_id = ? AND ativo = 1
        ORDER BY preferencial DESC, tempo_base_min ASC
        """,
        (origem_id, destino_id),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "origem_id": r[1],
            "destino_id": r[2],
            "modal": r[3],
            "descricao_percurso": r[4],
            "tempo_base_min": r[5],
            "sensibilidade_transito": r[6],
            "preferencial": bool(r[7]),
        }
        for r in rows
    ]
