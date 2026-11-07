from database.sqlite_db import get_connection


def obter_perfil():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            telefone_whatsapp,
            horario_chegada_padrao,
            tolerancia_atraso_min,
            alertas_padrao,
            antecedencia_pergunta_origem_min,
            dias_monitorados
        FROM user_profile
        ORDER BY id ASC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    alertas_lista = [
        int(x.strip())
        for x in (row[5] or "30,15,10,5,0").split(",")
        if x.strip().isdigit()
    ]

    return {
        "id": row[0],
        "nome": row[1],
        "telefone_whatsapp": row[2],
        "horario_chegada_padrao": row[3],
        "tolerancia_atraso_min": row[4],
        "alertas_padrao": row[5],
        "alertas_minutos_lista": sorted(alertas_lista, reverse=True),
        "antecedencia_pergunta_origem_min": row[6],
        "dias_monitorados": row[7],
    }


def atualizar_perfil(
    nome=None,
    telefone_whatsapp=None,
    horario_chegada_padrao=None,
    tolerancia_atraso_min=None,
    alertas_padrao=None,
    antecedencia_pergunta_origem_min=None,
    dias_monitorados=None,
):
    atual = obter_perfil()
    conn = get_connection()
    cursor = conn.cursor()

    if not atual:
        cursor.execute(
            """
            INSERT INTO user_profile (
                nome,
                telefone_whatsapp,
                horario_chegada_padrao,
                tolerancia_atraso_min,
                alertas_padrao,
                antecedencia_pergunta_origem_min,
                dias_monitorados
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome or "João",
                telefone_whatsapp,
                horario_chegada_padrao or "09:00",
                tolerancia_atraso_min if tolerancia_atraso_min is not None else 10,
                alertas_padrao or "30,15,10,5,0",
                antecedencia_pergunta_origem_min if antecedencia_pergunta_origem_min is not None else 45,
                dias_monitorados or "SEG,TER,QUA,QUI,SEX",
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE user_profile
            SET nome = ?,
                telefone_whatsapp = ?,
                horario_chegada_padrao = ?,
                tolerancia_atraso_min = ?,
                alertas_padrao = ?,
                antecedencia_pergunta_origem_min = ?,
                dias_monitorados = ?
            WHERE id = ?
            """,
            (
                nome if nome is not None else atual["nome"],
                telefone_whatsapp if telefone_whatsapp is not None else atual["telefone_whatsapp"],
                horario_chegada_padrao if horario_chegada_padrao is not None else atual["horario_chegada_padrao"],
                tolerancia_atraso_min if tolerancia_atraso_min is not None else atual["tolerancia_atraso_min"],
                alertas_padrao if alertas_padrao is not None else atual["alertas_padrao"],
                (
                    antecedencia_pergunta_origem_min
                    if antecedencia_pergunta_origem_min is not None
                    else atual["antecedencia_pergunta_origem_min"]
                ),
                dias_monitorados if dias_monitorados is not None else atual["dias_monitorados"],
                atual["id"],
            ),
        )

    conn.commit()
    conn.close()
    return obter_perfil()
