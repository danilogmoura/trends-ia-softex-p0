"""Integração offline do fluxo completo (Nível Avançado — item 3).

Fecha a lacuna apontada pela revisão da suíte (decisão 0.17): nenhum teste anterior
exercitava ``app.main()`` nem seus códigos de saída. Aqui o ciclo de 4 passos é
executado **ponta-a-ponta sem nenhuma chamada real ao LLM**, substituindo as
fronteiras externas por mocks leves via ``monkeypatch.setattr`` (padrão mais simples
que o fake-class de ``test_rede.py``, adequado a trocar dependências de módulo).

O que é mockado e por quê:
  - ``ler_entrada_terminal`` → devolve texto controlado (evita depender de stdin);
  - ``carregar_config`` → dict mínimo válido (evita ler ``.env``/ambiente real);
  - ``logs.configurar`` → no-op (evita criar ``logs/execucao.log`` durante os testes);
  - ``analisar_ingredientes`` → resposta falsa de sucesso, ou lança uma exceção de
    domínio para simular falha (substitui toda a rede).

Cobertos os cinco caminhos de saída de ``main()`` definidos no Intermediário
(decisão 0.14): feliz→0, entrada inválida→1, config ausente→2, erro de config→2,
falha de LLM→1, Ctrl+C→130. Nenhum deles toca a rede nem o provedor institucional.
"""

import pytest

from src import app
from src.erros import ErroDeConfiguracao, ErroDeLlm


CONFIG_MINIMA = {
    "base_url": "https://servidor-valido.test/v1",
    "api_key": "chave-falsa-de-teste",
    "model": "modelo-teste",
}


def _prepara_fluxo(monkeypatch, *, entrada="farinha, sal", resposta="ANALISE-FALSA"):
    """Instala os mocks das fronteiras e registra o que chegou em cada função."""
    chamado = {"analisar_com_entrada": None}

    monkeypatch.setattr(app, "ler_entrada_terminal", lambda: entrada)
    monkeypatch.setattr(app, "carregar_config", lambda: dict(CONFIG_MINIMA))
    # No-op: não queremos abrir arquivo de log nem tocar o logger global nos testes.
    monkeypatch.setattr(app.logs, "configurar", lambda *a, **k: None)

    def _fake_analisar(entrada_validada, config):
        chamado["analisar_com_entrada"] = entrada_validada
        return resposta

    monkeypatch.setattr(app, "analisar_ingredientes", _fake_analisar)
    return chamado


def test_fluxo_feliz_retorna_zero_e_apresenta_no_stdout(monkeypatch, capsys):
    """Ciclo completo com mocks: exit 0 e a análise aparece no stdout."""
    chamado = _prepara_fluxo(monkeypatch, entrada="  farinha de trigo, sal  ", resposta="  RESPOSTA DO MODELO  ")

    codigo = app.main()

    assert codigo == 0
    saida = capsys.readouterr().out
    assert "RESPOSTA DO MODELO" in saida
    assert "ANÁLISE DO RÓTULO" in saida
    # A entrada foi normalizada (bordas removidas) antes de chegar à análise.
    assert chamado["analisar_com_entrada"] == "farinha de trigo, sal"


def test_entrada_vazia_sai_um_sem_chamar_llm(monkeypatch, capsys):
    """Entrada só-espaços: ValueError ainda na validação → exit 1, análise jamais chamada."""
    chamado = _prepara_fluxo(monkeypatch, entrada="     \n  ")

    codigo = app.main()

    capturado = capsys.readouterr()
    assert codigo == 1
    assert "[entrada inválida]" in capturado.err
    assert chamado["analisar_com_entrada"] is None  # bloqueada antes da rede


def test_config_ausente_sai_dois(monkeypatch, capsys):
    """Configuração ausente (ConfiguracaoAusenteError) → exit 2, mensagem legível."""
    monkeypatch.setattr(app, "ler_entrada_terminal", lambda: "agua, sal")

    def _falha_config():
        raise app.ConfiguracaoAusenteError("Faltou LLM_API_KEY no ambiente.")

    monkeypatch.setattr(app, "carregar_config", _falha_config)

    codigo = app.main()

    capturado = capsys.readouterr()
    assert codigo == 2
    assert "[configuração]" in capturado.err


def test_erro_de_configuracao_formato_sai_dois(monkeypatch, capsys):
    """ErroDeConfiguracao (formato inválido) compartilha o exit 2 da config (decisão 0.14)."""
    monkeypatch.setattr(app, "ler_entrada_terminal", lambda: "agua, sal")

    def _falha_formato():
        raise ErroDeConfiguracao("A variável LLM_BASE_URL não contém uma URL válida.")

    monkeypatch.setattr(app, "carregar_config", _falha_formato)

    codigo = app.main()

    capturado = capsys.readouterr()
    assert codigo == 2
    assert "[configuração]" in capturado.err
    # A mensagem humana não pode ecoar a credencial.
    assert "chave-falsa-de-teste" not in capturado.err


def test_falha_de_llm_sai_um_com_mensagem_humana(monkeypatch, capsys):
    """Falha de comunicação (ErroDeLlm vinda da análise) → exit 1 + prefixo [LLM]."""
    _prepara_fluxo(monkeypatch)

    def _falha_llm(entrada_validada, config):
        raise ErroDeLlm("Não foi possível falar com o LLM — serviço indisponível.")

    monkeypatch.setattr(app, "analisar_ingredientes", _falha_llm)

    codigo = app.main()

    capturado = capsys.readouterr()
    assert codigo == 1
    assert "[LLM]" in capturado.err
    assert "indisponível" in capturado.err


def test_interrupcao_do_usuario_sai_cento_trinta(monkeypatch, capsys):
    """Ctrl+C (KeyboardInterrupt) durante a leitura → exit 130, sem stack trace."""
    def _interrompe():
        raise KeyboardInterrupt

    monkeypatch.setattr(app, "ler_entrada_terminal", _interrompe)

    codigo = app.main()

    capturado = capsys.readouterr()
    assert codigo == 130
    assert "interrompida" in capturado.err.lower()
