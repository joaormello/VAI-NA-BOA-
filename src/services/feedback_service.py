import re
from datetime import date, datetime
from database.sqlite_db import get_connection
from database.appointments_repository import (
    buscar_compromisso_por_id,
    obter_ou_criar_estado_diario,
)


def extrair_atraso_de_texto(texto):
    """
    Interpreta frases naturais enviadas no WhatsApp/Apple Watch como:
    - 'cheguei no horario' / 'cheguei na hora' / 'no horario' -> 0 min
    - 'cheguei 16 minutos atrasado' / 'atrasei 16 min' / '+16' -> +16 min
    - 'cheguei 10 min adiantado' / 'adiantado 10 min' / '-10' -> -10 min
    """
    txt = texto.lower().strip()

    if any(p in txt for p in ["no horario", "no horário", "na hora", "pontual", "em ponto"]):
        return 0

    match_num = re.search(r"([+-]?\d+)", txt)
    if not match_num:
        return 0

    valor = int(match_num.group(1))
    if any(p in txt for p in ["adiantado", "antes", "cedo"]) and valor > 0:
        return -valor

    if any(p in txt for p in ["atrasado", "atrasei", "atraso", "depois"]) and valor < 0:
        return abs(valor)

    return valor


def registrar_feedback_chegada(
    appointment_id,
    atraso_ou_texto,
    modal_utilizado=None,
    observacao=None,
    data_str=None,
):
    """
    Registra se o usuário chegou no horário ou atrasado no compromisso do dia
    e recalibra automaticamente o ajuste de aprendizado (ajuste_aprendizado_min)
    para corrigir os próximos horários de saída no banco.
    """
    if data_str is None:
        data_str = date.today().strftime("%Y-%m-%d")

    if isinstance(atraso_ou_texto, (int, float)):
        atraso_min = int(round(atraso_ou_texto))
    else:
        atraso_min = extrair_atraso_de_texto(str(atraso_ou_texto))

    obter_ou_criar_estado_diario(appointment_id, data_str)
    agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE appointment_daily_state
        SET chegada_confirmada = 1,
            atraso_real_min = ?,
            modal_utilizado = COALESCE(?, modal_utilizado),
            feedback_registrado_em = ?,
            observacao_feedback = COALESCE(?, observacao_feedback),
            status = 'CHEGOU'
        WHERE appointment_id = ? AND data = ?
        """,
        (atraso_min, modal_utilizado, agora_str, observacao, appointment_id, data_str),
    )

    # Recalibra o ajuste_aprendizado_min com base no histórico real de chegadas desse compromisso
    cursor.execute(
        """
        SELECT atraso_real_min
        FROM appointment_daily_state
        WHERE appointment_id = ? AND chegada_confirmada = 1 AND atraso_real_min IS NOT NULL
        ORDER BY data DESC
        LIMIT 10
        """,
        (appointment_id,),
    )
    historico_atrasos = [r[0] for r in cursor.fetchall()]

    # Dá peso maior ao feedback mais recente (70% média recente + 30% último evento se houve atraso)
    if historico_atrasos:
        media_atraso = sum(historico_atrasos) / len(historico_atrasos)
        ultimo = historico_atrasos[0]
        ajuste_calculado = round((media_atraso * 0.6) + (ultimo * 0.4))
        # Nunca reduz a margem abaixo de -5 min por segurança, mas compensa atrasos integralmente
        novo_ajuste = max(-5, ajuste_calculado)
    else:
        novo_ajuste = 0

    cursor.execute(
        """
        UPDATE appointments
        SET ajuste_aprendizado_min = ?
        WHERE id = ?
        """,
        (novo_ajuste, appointment_id),
    )

    conn.commit()
    conn.close()

    compromisso = buscar_compromisso_por_id(appointment_id)
    titulo = compromisso["titulo"] if compromisso else f"ID {appointment_id}"

    if atraso_min > 0:
        status_msg = f"⚠️ Chegada com *{atraso_min} min de atraso* registrada."
        acao_msg = (
            f"🧠 *Auto-ajuste ativado:* Adicionei *+{novo_ajuste} min* de compensação "
            f"inteligente no compromisso *{titulo}* para te avisar mais cedo nas próximas vezes!"
        )
    elif atraso_min < 0:
        status_msg = f"✅ Chegada com *{abs(atraso_min)} min de antecedência* registrada!"
        acao_msg = (
            f"🧠 *Calibração atual para {titulo}:* {'+' if novo_ajuste >= 0 else ''}{novo_ajuste} min."
        )
    else:
        status_msg = "🎯 Chegada *exatamente no horário previsto* registrada!"
        acao_msg = (
            f"🧠 *Calibração mantida para {titulo}:* {'+' if novo_ajuste >= 0 else ''}{novo_ajuste} min."
        )

    return {
        "appointment_id": appointment_id,
        "titulo": titulo,
        "atraso_registrado_min": atraso_min,
        "novo_ajuste_aprendizado_min": novo_ajuste,
        "total_feedbacks": len(historico_atrasos),
        "mensagem_resposta": f"{status_msg}\n{acao_msg}",
    }
