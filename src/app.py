"""Ponto de entrada do P0 — Primeiro fluxo com LLM.

Orquestra o ciclo de 4 passos exigido no Nível Básico:
  1. receber uma entrada textual (terminal);
  2. preparar e enviar a solicitação ao modelo;
  3. processar a resposta recebida;
  4. apresentar o resultado ao usuário.

Execução: ``python -m src.app``
"""

import sys

from .config import ConfiguracaoAusenteError, carregar_config
from .entrada import validar_entrada
from .llm import analisar_ingredientes


def ler_entrada_terminal() -> str:
    """Passo 1 — recebe o texto bruto do usuário pelo terminal.

    Lê linha a linha e encerra quando o usuário digita uma linha em branco.
    Evita depender de Ctrl+D, que só funciona em linha nova e varia entre
    terminais (WSL/Windows). Quando a entrada vem por pipe/redirecionamento
    (não é um terminal interativo), lê tudo de uma vez.
    """
    if not sys.stdin.isatty():
        return sys.stdin.read()

    print(
        "Cole a lista de ingredientes do rótulo.\n"
        "Quando terminar, deixe uma linha em branco e pressione Enter."
    )
    linhas: list[str] = []
    for linha in sys.stdin:
        if linha.strip() == "":
            break
        linhas.append(linha.rstrip("\n"))
    return "\n".join(linhas)


def main() -> int:
    try:
        bruto = ler_entrada_terminal()
        entrada = validar_entrada(bruto)          # passo 1 (validação)
        config = carregar_config()                 # configuração externa
        resposta = analisar_ingredientes(entrada, config)  # passos 2 e 3
        print("\n==================== ANÁLISE ====================\n")  # passo 4
        print(resposta if resposta.strip() else "(o modelo não retornou conteúdo)")
        return 0
    except ConfiguracaoAusenteError as erro:
        print(f"\n[configuração] {erro}", file=sys.stderr)
        return 2
    except ValueError as erro:
        print(f"\n[entrada inválida] {erro}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
