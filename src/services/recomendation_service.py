from analysis.traffic_analysis import(calcular_tempo_rota, total_consultas_rota)

def gerar_recomendacao_rota(origem, destino, tempo_atual):
    total = total_consultas_rota(origem, destino)

    if total <5:
        return(
            "⚠️ Histórico insuficiente "
            "para recomendações confiáveis."
        )

    media = calcular_tempo_rota(origem, destino)

    diferenca = (
        (tempo_atual - media)/media
        *100
    )

    if diferenca >=20 :
        return(
            "⚠️ Trânsito acima do normal. "
            "Considere sair mais cedo."
        )

    elif diferenca <=20:
        return(
            "✅ Trânsito melhor que o normal. "
            "Bom momento para viajar."
        )

    return(
        "👍 Condições dentro do padrão."
    )