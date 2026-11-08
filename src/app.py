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
from .llm import analisar_ingredientes, processar_resposta


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


def apresentar(resultado: str) -> None:
    """Passo 4 do ciclo — apresenta o resultado processado ao usuário.

    Isola a formatação da saída da orquestração em ``main()``: cabeçalho e corpo
    da análise. O aviso legal é emitido pelo próprio modelo no topo da resposta
    (decisão 0.9), então aqui não se repete. Se o texto vier vazio, sinaliza com
    clareza em vez de imprimir nada.
    """
    print("\n==================== ANÁLISE DO RÓTULO ====================")
    print()
    print(resultado.strip() if resultado.strip() else "(o modelo não retornou conteúdo)")


def main() -> int:
    try:
        bruto = ler_entrada_terminal()                     # passo 1
        entrada = validar_entrada(bruto)                   # passo 1 (validação)
        config = carregar_config()                         # configuração externa
        resposta_crua = analisar_ingredientes(entrada, config)  # passo 2
        resultado = processar_resposta(resposta_crua)      # passo 3
        apresentar(resultado)                              # passo 4
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
