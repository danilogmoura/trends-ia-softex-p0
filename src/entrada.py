"""Captura e validação da entrada textual.

Responsabilidade única: receber o texto bruto do rótulo de ingredientes e
garantir que é utilizável antes de qualquer chamada ao LLM.
"""

# Limite defensivo de tamanho da entrada. Um rótulo de ingredientes raramente
# passa de algumas centenas de caracteres; o teto existe para barrar, ANTES de
# consumir a API, colagens acidentais ou entradas abusivamente longas.
MAX_ENTRADA_CHARS = 5000


def validar_entrada(texto: str) -> str:
    """Valida e sanitiza a entrada textual vinda do terminal.

    Regras:
      - Bloqueia entrada vazia ou composta apenas por espaços, com orientação
        clara ao usuário (sem erro técnico extenso).
      - Barra texto excessivamente longo antes de consumir a API.

    Retorna o texto normalizado (espaços colapsados nas bordas e quebras de
    linha padronizadas), pronto para preparação da solicitação.

    Levanta ``ValueError`` com mensagem compreensível quando a entrada é
    inválida — nunca uma exceção técnica crua.
    """
    if not isinstance(texto, str):
        raise ValueError(
            "A entrada precisa ser um texto. Cole a lista de ingredientes da embalagem."
        )

    # Normaliza quebras de linha e remove espaços nas extremidades.
    normalizado = texto.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not normalizado:
        raise ValueError(
            "Nenhum ingrediente foi informado. Cole a lista de ingredientes "
            "presente na embalagem do produto (ex.: 'farinha de trigo, sal, ...')."
        )

    if len(normalizado) > MAX_ENTRADA_CHARS:
        raise ValueError(
            f"A entrada é longa demais ({len(normalizado)} caracteres, limite "
            f"{MAX_ENTRADA_CHARS}). Envie apenas a lista de ingredientes do rótulo, "
            "sem instruções de preparo ou outros textos da embalagem."
        )

    return normalizado

