from services.traffic_service import monitorar_rota
from analysis.traffic_analysis import (calcular_tempo_rota, melhor_tempo_rota, pior_tempo_rota, melhor_horario_rota, pior_horario_rota, comparar_com_media_rota)
from services.recomendation_service import gerar_recomendacao_rota
from analysis.traffic_analysis import calcular_horario_saida, calcular_horario_saida_seguro
from database.settings_repository import buscar_configuracoes

config = buscar_configuracoes()
horario_chegada = config[3]

def executar_pipeline(origem, destino):
    rota = monitorar_rota(origem, destino)

    relatorio = f"""
==================================================
                    VAI NA BOA
==================================================

📍 Distância atual: {rota['distancia_km']} km
⏱️ Tempo atual: {rota['tempo_minutos']} min

🎯 Horário desejado:
{horario_chegada}

🕑 Saída recomendada:
{calcular_horario_saida(
    origem, 
    destino,
    horario_chegada)}

🛡️ Saída segura:
  {calcular_horario_saida_seguro(
      origem, 
      destino,
      horario_chegada)}

📊 Tempo médio histórico:
{calcular_tempo_rota(origem, destino)} min

📈 Total de consultas:
{melhor_tempo_rota(origem, destino)} min

✅ Melhor tempo registrado:
{melhor_tempo_rota(origem, destino)} min

⚠️ Pior tempo registrado:
{pior_tempo_rota(origem, destino)} min

🕐 Melhor horário histórico:
{melhor_horario_rota(origem, destino)}:00

🚦 Pior horário histórico:
{pior_horario_rota(origem, destino)}:00

{comparar_com_media_rota(origem, destino, rota['tempo_minutos'])}

💡 RECOMENDAÇÃO

{gerar_recomendacao_rota(origem, destino, rota["tempo_minutos"])}

==================================================
"""

    return relatorio