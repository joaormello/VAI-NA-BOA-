from database.sqlite_db import get_connetcion

def salvar_configuracao(
        origem, 
        destino,
        horario_chegada
):
    conn = get_connetcion()
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


def listar_configuracoes():
    conn = get_connetcion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM settings
    """)

    configuracoes = cursor.fetchall()
    conn.close()
    return configuracoes


def buscar_configuracoes():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM settings
        LIMIT 1     
""")

    configuracao = cursor.fetchone()

    conn.close()
    return configuracao


def atualizar_configuracao(
        config_id,
        origem, 
        destino,
        horario_chegada
):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE settings
        SET origem = ?,
            destino = ?,
            horario_chegada = ?
        WHERE id = ?    
""",
(
    origem,
    destino,
    horario_chegada,
    config_id
))
    conn.commit()
    conn.close()


def excluir_configuracao(config_id):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM settings
        WHERE id = ?    
""",
(config_id,))

    conn.commit()
    conn.close()
    