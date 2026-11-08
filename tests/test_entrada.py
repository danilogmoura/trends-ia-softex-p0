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
