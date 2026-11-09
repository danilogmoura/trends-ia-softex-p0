"""Tratamento de resposta vazia / formato inesperado (Nível Intermediário — item 2).

Cenário 6 da matriz de erros. O checklist do Intermediário exige **tratar** a
resposta vazia ou em formato inesperado com mensagem compreensível; a decisão
0.12 separa isso do *teste offline puramente simulado*, que fica no Avançado.

Este arquivo exercita apenas o **tratamento**: uma resposta que chegou vazia
(corpo ausente) deve virar erro de domínio claro, e não passar silenciosa para a
apresentação. Falha de propósito porque importa `src.erros`, camada extraída no
item 3 (refactor) e preenchida com o tratamento no item 4 (feat).
"""

import pytest

from src import erros  # camada de tratamento ainda inexistente → torna este caso vermelho


def test_resposta_vazia_gera_erro_claro_sem_stack_trace():
    """Corpo vazio vindo da chamada real deve ser rejeitado como erro legível."""
    with pytest.raises(erros.ErroDeResposta) as excinfo:
        erros.validar_resposta("")
    assert str(excinfo.value).strip() != ""


def test_formato_inesperado_e_recusado():
    """Estrutura inesperada (sem choices/None) deve ser tratada, não propagada crua."""
    with pytest.raises(erros.ErroDeResposta):
        erros.validar_resposta(None)
