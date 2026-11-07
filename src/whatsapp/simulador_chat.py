"""
src/whatsapp/simulador_chat.py
Simulador de terminal para você testar como o WhatsApp e o Apple Watch vão responder.
"""
import sys
import os
from pathlib import Path

# Adiciona a pasta src ao sys.path para importação limpa
BASE_SRC = Path(__file__).resolve().parents[1]
if str(BASE_SRC) not in sys.path:
    sys.path.insert(0, str(BASE_SRC))

from whatsapp.bot_handler import processar_mensagem_whatsapp


def main():
    print("=" * 60)
    print("🤖 VAI NA BOA — SIMULADOR DE CHAT (WHATSAPP / APPLE WATCH)")
    print("=" * 60)
    print("Comandos disponíveis: /status, /sair, 1, 2, 'cheguei no horário', 'sair' para fechar\n")

    while True:
        try:
            texto = input("\n📱 Você (WhatsApp): ").strip()
            if not texto:
                continue
            if texto.lower() in ("sair", "exit", "quit"):
                print("Encerrando simulador... Até mais!")
                break

            resposta = processar_mensagem_whatsapp(texto)
            print("\n⌚ Vai na Boa:")
            print(resposta)
            print("-" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\nSaindo...")
            break


if __name__ == "__main__":
    main()
