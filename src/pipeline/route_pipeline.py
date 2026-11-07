from services.traffic_service import monitorar_rota
from analysis.traffic_analysis import (
    calcular_tempo_rota,
    melhor_tempo_rota,
    pior_tempo_rota,
    melhor_horario_rota,
    pior_horario_rota,
    comparar_com_media_rota,
    total_consultas_rota,
    calcular_horario_saida,
    calcular_horario_saida_seguro,
    calcular_risco_atraso,
    prever_piora_transito,
)
from services.recomendation_service import gerar_recomendacao_rota
from database.settings_repository import buscar_configuracoes


def executar_pipeline(origem, destino):
    config = buscar_configuracoes()
    horario_chegada = config[3] if config else "09:00"

    rota = monitorar_rota(origem, destino)
    risco = calcular_risco_atraso(
        origem,
        destino,
        horario_chegada=horario_chegada,
        tempo_atual=rota["tempo_minutos"],
    )
    previsao = prever_piora_transito(origem, destino)

    melhor_hr = melhor_horario_rota(origem, destino)
    pior_hr = pior_horario_rota(origem, destino)
    melhor_hr_str = f"{melhor_hr}:00" if melhor_hr is not None else "N/A"
    pior_hr_str = f"{pior_hr}:00" if pior_hr is not None else "N/A"

    osrm_str = (
        f" (TomTom: {rota['tempo_tomtom_min']}m | OSRM: {rota['tempo_osrm_min']}m)"
        if rota.get("tempo_osrm_min") is not None
        else ""
    )

    relatorio = f"""
==================================================
                    VAI NA BOA
==================================================

📍 Distância atual: {rota['distancia_km']} km
⏱️ Tempo consolidado: {rota['tempo_minutos']} min{osrm_str}

🎯 Horário desejado:
{horario_chegada}

🕑 Saída recomendada:
{calcular_horario_saida(origem, destino, horario_chegada)}

🛡️ Saída segura:
{calcular_horario_saida_seguro(origem, destino, horario_chegada)}

🎲 Risco de atraso:
{risco['mensagem']}

🔮 Previsão de trânsito:
{previsao}

📊 Tempo médio histórico:
{calcular_tempo_rota(origem, destino)} min

📈 Total de consultas:
{total_consultas_rota(origem, destino)}

✅ Melhor tempo registrado:
{melhor_tempo_rota(origem, destino)} min

⚠️ Pior tempo registrado:
{pior_tempo_rota(origem, destino)} min

🕐 Melhor horário histórico:
{melhor_hr_str}

🚦 Pior horário histórico:
{pior_hr_str}

{comparar_com_media_rota(origem, destino, rota['tempo_minutos'])}

💡 RECOMENDAÇÃO

{gerar_recomendacao_rota(origem, destino, rota["tempo_minutos"])}

==================================================
"""

    return relatorio
