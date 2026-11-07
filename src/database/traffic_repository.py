from datetime import datetime
from database.sqlite_db import get_connetcion
from database.location_repository import resolver_local_id


def salvar_historico(
    origem,
    destino,
    distancia_km,
    tempo_minutos,
):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    origem_id = resolver_local_id(origem, criar_se_nao_existir=True)
    destino_id = resolver_local_id(destino, criar_se_nao_existir=True)

    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO traffic_history(
            data_hora,
            origem_id,
            destino_id,
            distancia_km,
            tempo_minutos
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data_hora,
            origem_id,
            destino_id,
            distancia_km,
            tempo_minutos,
        ),
    )

    conn.commit()
    conn.close()


def listar_historico():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            th.id,
            th.data_hora,
            l_orig.apelido AS origem,
            l_dest.apelido AS destino,
            th.distancia_km,
            th.tempo_minutos
        FROM traffic_history th
        JOIN locations l_orig ON l_orig.id = th.origem_id
        JOIN locations l_dest ON l_dest.id = th.destino_id
        ORDER BY th.data_hora ASC
        """
    )

    historico = cursor.fetchall()
    conn.close()
    return historico


def listar_historico_rota(origem, destino):
    origem_id = resolver_local_id(origem, criar_se_nao_existir=False)
    destino_id = resolver_local_id(destino, criar_se_nao_existir=False)

    if origem_id is None or destino_id is None:
        return []

    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            th.id,
            th.data_hora,
            l_orig.apelido AS origem,
            l_dest.apelido AS destino,
            th.distancia_km,
            th.tempo_minutos
        FROM traffic_history th
        JOIN locations l_orig ON l_orig.id = th.origem_id
        JOIN locations l_dest ON l_dest.id = th.destino_id
        WHERE th.origem_id = ?
          AND th.destino_id = ?
        ORDER BY th.data_hora ASC
        """,
        (
            origem_id,
            destino_id,
        ),
    )

    historico = cursor.fetchall()
    conn.close()

    return historico
