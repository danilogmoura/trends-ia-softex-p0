"""Captura e validação da entrada textual.

Responsabilidade única: receber o texto bruto do rótulo de ingredientes e
garantir que é utilizável antes de qualquer chamada ao LLM.
"""


def validar_entrada(texto: str) -> str:
    """Valida e sanitiza a entrada textual vinda do terminal.

    Regras (a implementar no item 3):
      - Bloqueia entrada vazia ou composta apenas por espaços, com orientação
        clara ao usuário (sem erro técnico extenso).
      - Barra texto excessivamente longo antes de consumir a API.

    Retorna o texto normalizado pronto para preparação da solicitação.
    """
    # NotImplementedError é subclasse de RuntimeError; tipo neutro mantém o
    # estado 'vermelho' honesto até a implementação no item 3.
    raise AssertionError("validar_entrada será implementada no item 3 (feat)")
