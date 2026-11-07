from datetime import date, datetime
from database.sqlite_db import get_connection
from database.location_repository import resolver_local_id, buscar_local_por_id

MAPA_DIAS_SEMANA = {
    0: "SEG",
    1: "TER",
    2: "QUA",
    3: "QUI",
    4: "SEX",
    5: "SAB",
    6: "DOM",
}


def _normalizar_origens_alternativas(origens_alternativas):
    if not origens_alternativas:
        return None

    if isinstance(origens_alternativas, str):
        itens = [x.strip() for x in origens_alternativas.split(",") if x.strip()]
    else:
        itens = [str(x).strip() for x in origens_alternativas if str(x).strip()]

    ids_resolvidos = []
    for item in itens:
        if item.isdigit():
            ids_resolvidos.append(str(int(item)))
        else:
            loc_id = resolver_local_id(item, criar_se_nao_existir=True)
            ids_resolvidos.append(str(loc_id))

    return ",".join(ids_resolvidos) if ids_resolvidos else None


def _expandir_origens_possiveis(origem_id, origens_alternativas_str):
    ids = [origem_id]
    if origens_alternativas_str:
        for parte in origens_alternativas_str.split(","):
            parte = parte.strip()
            if parte.isdigit():
                oid = int(parte)
                if oid not in ids:
                    ids.append(oid)
            elif parte:
                oid = resolver_local_id(parte, criar_se_nao_existir=False)
                if oid and oid not in ids:
                    ids.append(oid)

    locais = []
    for oid in ids:
        reg = buscar_local_por_id(oid)
        if reg:
            locais.append({"id": reg[0], "apelido": reg[1], "endereco": reg[3]})
    return locais


def _formatar_compromisso(row):
    alertas_str = row[10] or "30,15,10,5,0"
    alertas_lista = sorted(
        [int(x.strip()) for x in alertas_str.split(",") if x.strip().isdigit()],
        reverse=True,
    )
    origens_possiveis = _expandir_origens_possiveis(row[2], row[3])
    ajuste_aprendizado = row[14] if len(row) > 14 and row[14] is not None else 0

    return {
        "id": row[0],
        "titulo": row[1],
        "origem_id": row[2],
        "origem_padrao": row[12],
        "origens_alternativas_raw": row[3],
        "origens_possiveis": origens_possiveis,
        "perguntar_origem": bool(row[4]),
        "destino_id": row[5],
        "destino": row[13],
        "horario_chegada": row[6],
        "dias_semana": row[7],
        "data_especifica": row[8],
        "margem_seguranca_min": row[9],
        "ajuste_aprendizado_min": ajuste_aprendizado,
        "alertas_minutos": alertas_str,
        "alertas_minutos_lista": alertas_lista,
        "ativo": bool(row[11]),
    }


def salvar_compromisso(
    titulo,
    origem,
    destino,
    horario_chegada,
    dias_semana="SEG,TER,QUA,QUI,SEX",
    data_especifica=None,
    origens_alternativas=None,
    perguntar_origem=False,
    margem_seguranca_min=10,
    alertas_minutos="30,15,10,5,0",
):
    origem_id = resolver_local_id(origem, criar_se_nao_existir=True)
    destino_id = resolver_local_id(destino, criar_se_nao_existir=True)
    alternativas_norm = _normalizar_origens_alternativas(origens_alternativas)

    if alternativas_norm and not perguntar_origem:
        perguntar_origem = True

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM appointments
        WHERE titulo = ? COLLATE NOCASE AND ativo = 1
        """,
        (titulo,),
    )
    existente = cursor.fetchone()
    if existente:
        cursor.execute(
            """
            UPDATE appointments
            SET origem_id = ?,
                origens_alternativas = ?,
                perguntar_origem = ?,
                destino_id = ?,
                horario_chegada = ?,
                dias_semana = ?,
                data_especifica = ?,
                margem_seguranca_min = ?,
                alertas_minutos = ?
            WHERE id = ?
            """,
            (
                origem_id,
                alternativas_norm,
                1 if perguntar_origem else 0,
                destino_id,
                horario_chegada,
                dias_semana,
                data_especifica,
                margem_seguranca_min,
                alertas_minutos,
                existente[0],
            ),
        )
        compromisso_id = existente[0]
    else:
        cursor.execute(
            """
            INSERT INTO appointments (
                titulo,
                origem_id,
                origens_alternativas,
                perguntar_origem,
                destino_id,
                horario_chegada,
                dias_semana,
                data_especifica,
                margem_seguranca_min,
                alertas_minutos,
                ativo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                titulo,
                origem_id,
                alternativas_norm,
                1 if perguntar_origem else 0,
                destino_id,
                horario_chegada,
                dias_semana,
                data_especifica,
                margem_seguranca_min,
                alertas_minutos,
            ),
        )
        compromisso_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return buscar_compromisso_por_id(compromisso_id)


def buscar_compromisso_por_id(compromisso_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            a.id,
            a.titulo,
            a.origem_id,
            a.origens_alternativas,
            a.perguntar_origem,
            a.destino_id,
            a.horario_chegada,
            a.dias_semana,
            a.data_especifica,
            a.margem_seguranca_min,
            a.alertas_minutos,
            a.ativo,
            l_orig.apelido AS origem_apelido,
            l_dest.apelido AS destino_apelido,
            a.ajuste_aprendizado_min
        FROM appointments a
        JOIN locations l_orig ON l_orig.id = a.origem_id
        JOIN locations l_dest ON l_dest.id = a.destino_id
        WHERE a.id = ?
        """,
        (compromisso_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return _formatar_compromisso(row) if row else None


def buscar_compromisso_por_titulo(titulo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM appointments
        WHERE titulo LIKE ? AND ativo = 1
        ORDER BY id ASC LIMIT 1
        """,
        (f"%{titulo}%",),
    )
    row = cursor.fetchone()
    conn.close()
    return buscar_compromisso_por_id(row[0]) if row else None


def listar_compromissos(apenas_ativos=True):
    conn = get_connection()
    cursor = conn.cursor()

    filtro = "WHERE a.ativo = 1" if apenas_ativos else ""
    cursor.execute(
        f"""
        SELECT
            a.id,
            a.titulo,
            a.origem_id,
            a.origens_alternativas,
            a.perguntar_origem,
            a.destino_id,
            a.horario_chegada,
            a.dias_semana,
            a.data_especifica,
            a.margem_seguranca_min,
            a.alertas_minutos,
            a.ativo,
            l_orig.apelido AS origem_apelido,
            l_dest.apelido AS destino_apelido,
            a.ajuste_aprendizado_min
        FROM appointments a
        JOIN locations l_orig ON l_orig.id = a.origem_id
        JOIN locations l_dest ON l_dest.id = a.destino_id
        {filtro}
        ORDER BY a.horario_chegada ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return [_formatar_compromisso(r) for r in rows]


def listar_compromissos_do_dia(data_ref=None):
    if data_ref is None:
        hoje = date.today()
    elif isinstance(data_ref, str):
        hoje = datetime.strptime(data_ref, "%Y-%m-%d").date()
    else:
        hoje = data_ref

    data_str = hoje.strftime("%Y-%m-%d")
    dia_sigla = MAPA_DIAS_SEMANA[hoje.weekday()]

    todos = listar_compromissos(apenas_ativos=True)
    compromissos_hoje = []

    for comp in todos:
        if comp["data_especifica"] == data_str:
            compromissos_hoje.append(comp)
        elif not comp["data_especifica"] and comp["dias_semana"]:
            dias = [d.strip().upper() for d in comp["dias_semana"].split(",")]
            if dia_sigla in dias or "TODOS" in dias:
                compromissos_hoje.append(comp)

    return compromissos_hoje


def obter_ou_criar_estado_diario(appointment_id, data_str=None):
    if data_str is None:
        data_str = date.today().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO appointment_daily_state (
            appointment_id,
            data,
            status
        )
        VALUES (?, ?, 'PENDENTE')
        """,
        (appointment_id, data_str),
    )
    conn.commit()

    cursor.execute(
        """
        SELECT
            s.id,
            s.appointment_id,
            s.data,
            s.origem_escolhida_id,
            l.apelido,
            s.origem_perguntada,
            s.alertas_enviados,
            s.horario_saida_calculado,
            s.status,
            s.chegada_confirmada,
            s.atraso_real_min,
            s.modal_utilizado
        FROM appointment_daily_state s
        LEFT JOIN locations l ON l.id = s.origem_escolhida_id
        WHERE s.appointment_id = ? AND s.data = ?
        """,
        (appointment_id, data_str),
    )
    row = cursor.fetchone()
    conn.close()

    alertas_enviados = [
        int(x.strip())
        for x in (row[6] or "").split(",")
        if x.strip().isdigit()
    ]

    return {
        "id": row[0],
        "appointment_id": row[1],
        "data": row[2],
        "origem_escolhida_id": row[3],
        "origem_escolhida_apelido": row[4],
        "origem_perguntada": bool(row[5]),
        "alertas_enviados": alertas_enviados,
        "horario_saida_calculado": row[7],
        "status": row[8],
        "chegada_confirmada": bool(row[9]),
        "atraso_real_min": row[10],
        "modal_utilizado": row[11],
    }


def definir_origem_do_dia(appointment_id, origem, data_str=None):
    if data_str is None:
        data_str = date.today().strftime("%Y-%m-%d")

    obter_ou_criar_estado_diario(appointment_id, data_str)
    origem_id = resolver_local_id(origem, criar_se_nao_existir=False)
    if origem_id is None:
        raise ValueError(f"Origem '{origem}' não encontrada nos locais cadastrados.")

    conn = get_connection()
    conn.execute(
        """
        UPDATE appointment_daily_state
        SET origem_escolhida_id = ?,
            origem_perguntada = 1,
            status = 'EM_CONTAGEM'
        WHERE appointment_id = ? AND data = ?
        """,
        (origem_id, appointment_id, data_str),
    )
    conn.commit()
    conn.close()
    return obter_ou_criar_estado_diario(appointment_id, data_str)


def marcar_pergunta_origem_enviada(appointment_id, data_str=None):
    if data_str is None:
        data_str = date.today().strftime("%Y-%m-%d")

    obter_ou_criar_estado_diario(appointment_id, data_str)
    conn = get_connection()
    conn.execute(
        """
        UPDATE appointment_daily_state
        SET origem_perguntada = 1,
            status = 'AGUARDANDO_ORIGEM'
        WHERE appointment_id = ? AND data = ?
        """,
        (appointment_id, data_str),
    )
    conn.commit()
    conn.close()


def registrar_alerta_enviado(appointment_id, minutos_antes, horario_saida_calculado=None, data_str=None):
    if data_str is None:
        data_str = date.today().strftime("%Y-%m-%d")

    estado = obter_ou_criar_estado_diario(appointment_id, data_str)
    enviados = estado["alertas_enviados"]
    if minutos_antes not in enviados:
        enviados.append(minutos_antes)

    enviados_str = ",".join(str(x) for x in sorted(enviados, reverse=True))
    novo_status = "SAIU" if minutos_antes == 0 else "EM_CONTAGEM"

    conn = get_connection()
    conn.execute(
        """
        UPDATE appointment_daily_state
        SET alertas_enviados = ?,
            horario_saida_calculado = COALESCE(?, horario_saida_calculado),
            status = ?
        WHERE appointment_id = ? AND data = ?
        """,
        (enviados_str, horario_saida_calculado, novo_status, appointment_id, data_str),
    )
    conn.commit()
    conn.close()
    return obter_ou_criar_estado_diario(appointment_id, data_str)


def desativar_compromisso(compromisso_id):
    conn = get_connection()
    conn.execute("UPDATE appointments SET ativo = 0 WHERE id = ?", (compromisso_id,))
    conn.commit()
    conn.close()
