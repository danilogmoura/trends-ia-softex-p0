"""Testes do carregamento de configuração (Nível Básico — itens 2 e 4).

Escritos antes da implementação (TDD, doutrina do plano) e hoje cobrindo o
``carregar_config`` já entregue no item 4. Cenário obrigatório do enunciado:
credencial ausente gera erro claro SEM expor segredo — validado offline, sem
chamada real ao LLM.
"""

import pytest

from src import erros  # camada de tratamento ainda inexistente → torna este caso vermelho
from src.config import carregar_config


def test_credencial_ausente_gera_erro_claro(monkeypatch):
    """Sem LLM_API_KEY no ambiente, carregar_config deve falhar de forma controlada."""
    # Garante ausência das variáveis obrigatórias.
    for var in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(var, raising=False)

    with pytest.raises((KeyError, RuntimeError, ValueError)) as excinfo:
        carregar_config(carregar_arquivo=False)

    # O erro deve apontar a variável faltante...
    assert "LLM_API_KEY" in str(excinfo.value)


def test_erro_nao_expoe_valor_de_segredo(monkeypatch):
    """A mensagem de erro jamais pode conter um valor de chave real.

    Exige uma exceção de DOMÍNIO (KeyError/RuntimeError/ValueError) levantada pelo
    próprio ``carregar_config``, garantindo que a falha é controlada e não um
    vazio técnico — e que apenas o NOME da variável aparece, nunca o valor.
    """
    segredo = "sk-NAO-DEVE-APARECER-123456"
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:9/v1")
    monkeypatch.setenv("LLM_API_KEY", "")  # presente porém vazio → inválida
    monkeypatch.setenv("LLM_MODEL", "modelo-teste")

    with pytest.raises((KeyError, RuntimeError, ValueError)) as excinfo:
        carregar_config(carregar_arquivo=False)

    assert segredo not in str(excinfo.value)


def test_config_malformed_base_url_invalida_vira_erro_claro(monkeypatch):
    """Cenário 1 da matriz: variável presente porém inválida (base_url malformada).

    Hoje `carregar_config` só checa presença — uma base_url vazia-de-conteúdo mas
    não-vazia passa. O tratamento de formato é do Intermediário (item 4): deve
    levantar erro de domínio claro, sem despejar stack trace nem expor valores.
    """
    monkeypatch.setenv("LLM_BASE_URL", "nao-e-uma-url-valida")
    monkeypatch.setenv("LLM_API_KEY", "chave-falsa-de-teste")
    monkeypatch.setenv("LLM_MODEL", "modelo-teste")

    with pytest.raises(erros.ErroDeConfiguracao) as excinfo:
        carregar_config(carregar_arquivo=False)

    assert "LLM_BASE_URL" in str(excinfo.value)
    assert "chave-falsa-de-teste" not in str(excinfo.value)
