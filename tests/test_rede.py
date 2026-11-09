"""Bateria vermelha da matriz de erros (Nível Intermediário — item 2).

Escritos **antes** do tratamento, conforme a doutrina TDD do plano e a decisão
0.13. Cobrem os cenários de comunicação com o LLM que o checklist do
`AGENTS.md` exige tratar no Intermediário:

- credencial inválida (a API devolve 401);
- indisponibilidade do LLM (5xx ou conexão recusada);
- timeout (estouro de prazo).

Nenhum deles toca a rede real: substituímos o cliente OpenAI por um *fake* que
lança as exceções verdadeiras da biblioteca `openai`. Os testes falham de
propósito porque importam `src.erros`, camada de tradução de exceções extraída no
item 3 (refactor) e preenchida no item 4 (feat). Enquanto `src/erros.py` não
existir, a suíte inteira está vermelha pelo motivo correto (ImportError), sem
máscara.

Fronteira com o Avançado (decisão 0.12): aqui só se exercita o **tratamento**;
o mock offline completo de resposta ausente/vazia fica reservado ao item 3 do
Avançado.
"""

import httpx
import pytest
from openai import APIConnectionError, APITimeoutError, AuthenticationError

# Importação-alvo: ainda não existe — é exatamente isto que torna a bateria vermelha.
from src import erros


def _req():
    """Request httpx mínimo para construir as exceções reais da lib openai."""
    return httpx.Request("POST", "http://localhost:9/v1/chat/completions")


class _ClienteQueFalha:
    """Cliente fake cuja chamada de completion lança a exceção dada."""

    def __init__(self, exc):
        self._exc = exc
        completions = self._Completions(exc)
        chat = type("_Chat", (), {"completions": completions})()
        self.chat = chat

    class _Completions:
        def __init__(self, exc):
            self._exc = exc

        def create(self, *args, **kwargs):
            raise self._exc


CONFIG_FAKE = {
    "base_url": "http://localhost:9/v1",
    "api_key": "chave-falsa-de-teste",
    "model": "modelo-teste",
}
MENSAGENS = [{"role": "user", "content": "água, sal"}]


def test_credencial_invalida_vira_erro_de_autenticacao_legivel():
    """401 da API deve virar erro de autenticação claro, sem ecoar a chave."""
    exc = AuthenticationError("invalid api key", response=httpx.Response(401, request=_req()), body=None)
    with pytest.raises(erros.ErroDeAutenticacao) as excinfo:
        erros.chamar_llm(_ClienteQueFalha(exc), CONFIG_FAKE, MENSAGENS)
    # A mensagem humana não pode conter a credencial usada na config.
    assert "chave-falsa-de-teste" not in str(excinfo.value)


def test_indisponibilidade_orienta_tentar_mais_tarde():
    """Conexão recusada (indisponibilidade) deve orientar nova tentativa, sem stack trace crua."""
    exc = APIConnectionError(request=_req())
    with pytest.raises(erros.ErroIndisponibilidade) as excinfo:
        erros.chamar_llm(_ClienteQueFalha(exc), CONFIG_FAKE, MENSAGENS)
    assert str(excinfo.value).strip() != ""


def test_timeout_e_distinto_de_queda_de_conexao():
    """Timeout deve mapear para classe própria, distinguindo-se de indisponibilidade."""
    exc = APITimeoutError(request=_req())
    with pytest.raises(erros.ErroTimeout) as excinfo:
        erros.chamar_llm(_ClienteQueFalha(exc), CONFIG_FAKE, MENSAGENS)
    # Timeout NÃO deve ser tratado como indisponibilidade genérica.
    assert not isinstance(excinfo.value, erros.ErroIndisponibilidade)


# --- Nível Avançado, item 1: chamar_llm repassa os parâmetros de geração ---


class _ClienteQueRegistra:
    """Cliente fake que grava os kwargs da chamada e devolve uma resposta mínima válida."""

    def __init__(self):
        self.kwargs: dict = {}
        completions = self._Completions(self)
        chat = type("_Chat", (), {"completions": completions})()
        self.chat = chat

    class _Completions:
        def __init__(self, dono):
            self._dono = dono

        def create(self, *args, **kwargs):
            self._dono.kwargs = kwargs
            mensagem = type("_Msg", (), {"content": "ok"})()
            escolha = type("_Choice", (), {"message": mensagem})()
            return type("_Resp", (), {"choices": [escolha]})()


def test_parametros_presentes_sao_repassados():
    """max_tokens/temperature no config devem chegar ao create() do cliente."""
    cliente = _ClienteQueRegistra()
    config = {**CONFIG_FAKE, "max_tokens": 512, "temperature": 0.3}

    erros.chamar_llm(cliente, config, MENSAGENS)

    assert cliente.kwargs["max_tokens"] == 512
    assert cliente.kwargs["temperature"] == pytest.approx(0.3)


def test_parametros_ausentes_nao_sao_enviados():
    """Sem os opcionais no config, create() não recebe os campos (usa padrão do provedor)."""
    cliente = _ClienteQueRegistra()

    erros.chamar_llm(cliente, dict(CONFIG_FAKE), MENSAGENS)

    assert "max_tokens" not in cliente.kwargs
    assert "temperature" not in cliente.kwargs
