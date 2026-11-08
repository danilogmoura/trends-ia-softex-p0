"""Testes da validação de entrada (Nível Básico — item 2).

Doutrina do plano: todo requisito determinístico tem teste escrito ANTES do
código. Estes casos falham de propósito até o item 3 implementar ``validar_entrada``.
"""

import pytest

from src.entrada import validar_entrada


def test_entrada_vazia_e_bloqueada_com_orientacao():
    """Entrada vazia deve ser recusada com mensagem compreensível, não exceção crua."""
    with pytest.raises(ValueError) as excinfo:
        validar_entrada("")
    # A mensagem precisa orientar o usuário, não apenas dizer "vazio".
    assert "ingredientes" in str(excinfo.value).lower()


def test_entrada_so_espacos_e_bloqueada():
    """Só espaços/quebras de linha equivale a entrada vazia e deve ser bloqueado."""
    with pytest.raises(ValueError):
        validar_entrada("     \n\t   ")


def test_entrada_valida_e_normalizada():
    """Caso feliz: rótulo real volta com bordas e quebras normalizadas, sem erro."""
    bruto = "  farinha de trigo, sal,\r\n caseinato de calcio  "
    resultado = validar_entrada(bruto)
    # Bordas removidas e \r\n padronizado para \n; conteúdo interno (inclusive o
    # espaço após a quebra) é preservado — a normalização não reescreve o rótulo.
    assert resultado == "farinha de trigo, sal,\n caseinato de calcio"


def test_texto_excessivamente_longo_e_barrado_antes_da_api():
    """Sanitização pré-envio: texto acima do limite é recusado sem consumir a API."""
    from src.entrada import MAX_ENTRADA_CHARS

    longo = "acucar" * (MAX_ENTRADA_CHARS // 6 + 1)
    with pytest.raises(ValueError) as excinfo:
        validar_entrada(longo)
    assert "longa demais" in str(excinfo.value).lower()
