from analysis.traffic_analysis import (
    calcular_tempo_rota,
    total_consultas_rota,
    calcular_risco_atraso,
    prever_piora_transito,
)
from database.route_alternatives_repository import listar_alternativas_rota
from database.location_repository import buscar_local_por_apelido
from api.multimodal_provider import consultar_transporte_publico_google


def gerar_recomendacao_rota(origem, destino, tempo_atual):
    total = total_consultas_rota(origem, destino)

    if total < 5:
        base_msg = (
            "⚠️ Histórico insuficiente "
            "para recomendações estatísticas completas."
        )
    else:
        media = calcular_tempo_rota(origem, destino)
        diferenca = ((tempo_atual - media) / media) * 100

        if diferenca >= 20:
            base_msg = (
                "⚠️ Trânsito acima do normal nas vias. "
                "Considere sair mais cedo ou priorizar o Metrô."
            )
        elif diferenca <= -20:
            base_msg = (
                "✅ Trânsito melhor que o normal nas vias. "
                "Bom momento para viajar."
            )
        else:
            base_msg = "👍 Condições nas vias dentro do padrão."

    modal_rec = recomendar_melhor_modal_e_rota(origem, destino, tempo_vias_atual=tempo_atual)
    if modal_rec["resumo_formatado"]:
        return f"{base_msg}\n\n{modal_rec['resumo_formatado']}"

    return base_msg


def recomendar_melhor_modal_e_rota(origem, destino, tempo_vias_atual=None):
    """
    Avalia as opções de caminho/modal cadastradas para a rota (ex: Ônibus 746C-10 + 8605-10,
    Metrô, Carro) + Google Transit API (se disponível) e pondera pelo trânsito atual nas ruas.
    Se o trânsito de rua estiver pesado, recomenda automaticamente migrar para o Metrô!
    """
    media_vias = calcular_tempo_rota(origem, destino)
    if tempo_vias_atual and media_vias > 0:
        fator_transito_rua = max(0.8, tempo_vias_atual / media_vias)
    else:
        fator_transito_rua = 1.0

    alternativas_db = listar_alternativas_rota(origem, destino)
    opcoes_calculadas = []

    for alt in alternativas_db:
        sens = alt["sensibilidade_transito"]
        # Se fator_transito_rua = 1.30 (+30% de trânsito):
        # - Ônibus/Carro (sensibilidade 1.0) sofre +30% no tempo
        # - Metrô (sensibilidade 0.15) sofre apenas +4.5% no tempo!
        multiplicador = 1.0 + ((fator_transito_rua - 1.0) * sens)
        tempo_ajustado = round(alt["tempo_base_min"] * multiplicador)

        icone = (
            "🚇" if "METRO" in alt["modal"]
            else ("🚌" if "ONIBUS" in alt["modal"] else "🚗")
        )
        opcoes_calculadas.append(
            {
                "modal": alt["modal"],
                "icone": icone,
                "descricao": alt["descricao_percurso"],
                "tempo_base_min": alt["tempo_base_min"],
                "tempo_estimado_hoje_min": tempo_ajustado,
                "preferencial": alt["preferencial"],
            }
        )

    # Se houver chave do Google Maps configurada, também consulta opções ao vivo da SPTrans/Metrô
    loc_orig = buscar_local_por_apelido(origem)
    loc_dest = buscar_local_por_apelido(destino)
    if loc_orig and loc_dest and loc_orig[4] and loc_dest[4]:
        opcoes_google = consultar_transporte_publico_google(
            loc_orig[4], loc_orig[5], loc_dest[4], loc_dest[5]
        )
        for og in opcoes_google:
            icone = "🚇" if "METRO" in og["modal"] else "🚌"
            opcoes_calculadas.append(
                {
                    "modal": og["modal"],
                    "icone": icone,
                    "descricao": f"{og['descricao_percurso']} (Google Live)",
                    "tempo_base_min": og["tempo_estimado_min"],
                    "tempo_estimado_hoje_min": og["tempo_estimado_min"],
                    "preferencial": False,
                }
            )

    if not opcoes_calculadas:
        return {"melhor_opcao": None, "opcoes": [], "resumo_formatado": ""}

    # Ordena pela opção mais rápida hoje
    opcoes_ordenadas = sorted(
        opcoes_calculadas,
        key=lambda x: (x["tempo_estimado_hoje_min"], not x["preferencial"]),
    )
    melhor = opcoes_ordenadas[0]

    linhas = ["🧭 *OPÇÕES DE CAMINHO E MODAL HOJE:*"]
    for op in opcoes_ordenadas:
        destaque = " ⭐ *(Mais rápido)*" if op is melhor else ""
        linhas.append(
            f"  {op['icone']} *{op['descricao']}*: ~*{op['tempo_estimado_hoje_min']} min*{destaque}"
        )

    if fator_transito_rua >= 1.15 and "METRO" in melhor["modal"]:
        aumento_rua_pct = round((fator_transito_rua - 1.0) * 100)
        linhas.append(
            f"\n💡 *Dica Inteligente:* Trânsito nas ruas está +{aumento_rua_pct}% mais lento. "
            f"Hoje vá de *{melhor['descricao']}* para fugir do congestionamento!"
        )
    else:
        linhas.append(
            f"\n💡 *Melhor caminho hoje:* {melhor['icone']} *{melhor['descricao']}* (~{melhor['tempo_estimado_hoje_min']} min)."
        )

    return {
        "melhor_opcao": melhor,
        "opcoes": opcoes_ordenadas,
        "fator_transito_rua": round(fator_transito_rua, 2),
        "resumo_formatado": "\n".join(linhas),
    }
