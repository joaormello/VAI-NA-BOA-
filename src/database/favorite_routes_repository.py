from database.sqlite_db import get_connetcion

def salvar_rota_favorita(origem, destino):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM favorite_routes
        WHERE origem = ?
        AND destino = ?
    """, (origem, destino))
    rota_existente = cursor.fetchone()

    if rota_existente:
        print(
            f"⚠️ Rota {origem} -> {destino} já cadastrada."
        )
        conn.close()
        return

    cursor.execute("""
        INSERT INTO favorite_routes(
            origem, 
            destino
        )
        VALUES (?, ?)
    """, (origem, destino))

    conn.commit()
    conn.close()

    print(
        f"✅ Rota {origem} -> {destino} cadastrada."
    )


def listar_rotas_favoritas():
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM favorite_routes
        WHERE ativo = 1
    """)

    rotas = cursor.fetchall()

    conn.close()
    return rotas


def desativar_rotas(rota_id):
    conn = get_connetcion()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE favorite_routes
        SET ativo = 0
        WHERE id = ?
    """, (rota_id,))

    conn.commit()
    conn.close()


def limpar_rotas_favoritas():
    conn = get_connetcion()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM favorite_routes    
    """)

    conn.commit()
    conn.close()
