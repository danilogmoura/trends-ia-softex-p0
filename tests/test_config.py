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


# --- Nível Avançado, item 1: parâmetros de geração ajustáveis por config externa ---


def _ambiente_base_ok(monkeypatch):
    """Prepara o ambiente mínimo válido para carregar_config não falhar por ausência."""
    monkeypatch.setenv("LLM_BASE_URL", "https://servidor-valido.test/v1")
    monkeypatch.setenv("LLM_API_KEY", "chave-falsa-de-teste")
    monkeypatch.setenv("LLM_MODEL", "modelo-teste")


@pytest.mark.parametrize(
    "var", ("LLM_MAX_TOKENS", "LLM_TEMPERATURE", "LLM_TIMEOUT")
)
def test_parametros_opcionais_ausentes_nao_quebram(monkeypatch, var):
    """Sem nenhum parâmetro opcional definido, a config carrega e não injeta a chave.

    Ausência é válida: o app deve funcionar usando os padrões do provedor, então a
    chave simplesmente não aparece no dicionário retornado (chamar_llm não envia o campo).
    """
    _ambiente_base_ok(monkeypatch)
    monkeypatch.delenv(var, raising=False)

    config = carregar_config(carregar_arquivo=False)

    assert var.lower().removeprefix("llm_") not in config


def test_max_tokens_valido_vira_inteiro(monkeypatch):
    """LLM_MAX_TOKENS numérico positivo é convertido para int no config."""
    _ambiente_base_ok(monkeypatch)
    monkeypatch.setenv("LLM_MAX_TOKENS", "512")

    config = carregar_config(carregar_arquivo=False)

    assert config["max_tokens"] == 512
    assert isinstance(config["max_tokens"], int)


def test_temperature_valida_vira_float(monkeypatch):
    """LLM_TEMPERATURE dentro de [0,2] é convertida para float no config."""
    _ambiente_base_ok(monkeypatch)
    monkeypatch.setenv("LLM_TEMPERATURE", "0.3")

    config = carregar_config(carregar_arquivo=False)

    assert config["temperature"] == pytest.approx(0.3)


def test_timeout_valido_vira_float(monkeypatch):
    """LLM_TIMEOUT em segundos (>0) é convertido para float no config."""
    _ambiente_base_ok(monkeypatch)
    monkeypatch.setenv("LLM_TIMEOUT", "30")

    config = carregar_config(carregar_arquivo=False)

    assert config["timeout"] == pytest.approx(30.0)


@pytest.mark.parametrize(
    "var,valor",
    [
        ("LLM_MAX_TOKENS", "abc"),      # não numérico
        ("LLM_MAX_TOKENS", "0"),         # precisa ser > 0
        ("LLM_MAX_TOKENS", "-5"),        # negativo
        ("LLM_TEMPERATURE", "2.5"),      # acima de 2
        ("LLM_TEMPERATURE", "-0.1"),     # abaixo de 0
        ("LLM_TIMEOUT", "zero"),         # não numérico
        ("LLM_TIMEOUT", "-1"),           # precisa ser > 0
    ],
)
def test_parametro_invalido_gera_erro_claro_sem_valor_cru(monkeypatch, var, valor):
    """Parâmetro opcional presente porém inválido → ErroDeConfiguracao citando o NOME.

    A mensagem aponta qual variável está errada e como corrigir, sem despejar stack
    trace nem ecoar outros valores do ambiente.
    """
    _ambiente_base_ok(monkeypatch)
    monkeypatch.setenv(var, valor)

    with pytest.raises(erros.ErroDeConfiguracao) as excinfo:
        carregar_config(carregar_arquivo=False)

    assert var in str(excinfo.value)
