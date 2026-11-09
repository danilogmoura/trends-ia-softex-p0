"""Testes da camada de registros de execução (Nível Avançado — item 2).

O enunciado pede "registros simples que ajudem a compreender a execução, sem
armazenar chaves, tokens, credenciais, dados pessoais ou conteúdo sensível
desnecessário". Estes testes travam exatamente essa fronteira: verificam que o
resumo de uma chamada contém métricas e modelo, mas **jamais** a chave, a base
URL real, a entrada do usuário ou o texto devolvido pelo modelo. Tudo roda
offline, sem chamada real ao LLM.
"""

from src import logs


def test_resumo_de_chamada_contem_metricas_sem_conteudo():
    """O resumo traz duração, tamanho e nº de mensagens — nunca o texto em si."""
    resumo = logs.resumo_de_chamada(
        model="modelo-teste",
        duracao_ms=1234,
        n_mensagens=2,
        chars_resposta=567,
    )

    assert "modelo-teste" in resumo
    assert "1234" in resumo
    assert "567" in resumo
    assert "2" in resumo


def test_configuracao_para_log_omita_segredo_e_endpoint():
    """A representação usada p/ log expõe só o modelo; nunca api_key nem base_url."""
    registro = logs.configuracao_para_log(
        {
            "base_url": "https://servidor-secreto.test/v1",
            "api_key": "sk-NAO-DEVE-APARECER-9999",
            "model": "modelo-teste",
            "max_tokens": 512,
            "temperature": 0.3,
            "timeout": 30.0,
        }
    )

    assert "modelo-teste" in registro
    # Parâmetros de geração não são sensíveis e ajudam diagnóstico: podem aparecer.
    assert "512" in registro
    # Segredos e endpoint real são proibidos no registro.
    assert "sk-NAO-DEVE-APARECER-9999" not in registro
    assert "api_key" not in registro
    assert "servidor-secreto.test" not in registro
    assert "base_url" not in registro


def test_nivel_por_defeito_e_info(monkeypatch):
    """Sem LLM_LOG_LEVEL no ambiente, o nível efetivo é INFO."""
    monkeypatch.delenv("LLM_LOG_LEVEL", raising=False)
    assert logs.nivel_efetivo() == "INFO"


def test_nivel_invalido_recebe_aviso_e_usa_info(capsys, monkeypatch):
    """LLM_LOG_LEVEL inválido não derruba o app: avisa no stderr e cai em INFO."""
    monkeypatch.setenv("LLM_LOG_LEVEL", "GRITA")
    assert logs.nivel_efetivo() == "INFO"
    err = capsys.readouterr().err
    assert "LLM_LOG_LEVEL" in err
    assert "GRITA" not in err  # ecoa o nome da variável, não o valor cru inválido


def test_resolver_caminho_precedencia(monkeypatch, tmp_path):
    """Argumento explícito vence LLM_LOG_FILE, que vence o padrão gitignored."""
    monkeypatch.delenv("LLM_LOG_FILE", raising=False)
    assert logs._resolver_caminho(None) == logs._CAMINHO_PADRAO
    assert logs._resolver_caminho("meu.log") == "meu.log"

    monkeypatch.setenv("LLM_LOG_FILE", str(tmp_path / "env.log"))
    assert logs._resolver_caminho(None) == str(tmp_path / "env.log")
    # argumento explícito ainda vence o env
    assert logs._resolver_caminho("explicito.log") == "explicito.log"


def test_configurar_escreve_em_arquivo_sem_segredo(tmp_path, monkeypatch):
    """Após configurar(), o registro vai para o arquivo e nunca contém segredo."""
    # Zera handlers para simular uma execução nova (configurar é idempotente).
    for manipulador in list(logs.LOG.handlers):
        logs.LOG.removeHandler(manipulador)
        manipulador.close()
    monkeypatch.delenv("LLM_LOG_FILE", raising=False)

    destino = tmp_path / "sub" / "execucao.log"
    logs.configurar("DEBUG", str(destino))
    logs.LOG.info(
        logs.resumo_de_chamada(
            model="modelo-teste", duracao_ms=10, n_mensagens=2, chars_resposta=99
        )
    )
    logs.LOG.info(
        logs.configuracao_para_log(
            {
                "model": "modelo-teste",
                "api_key": "sk-NAO-DEVE-APARECER-9999",
                "base_url": "https://servidor-secreto.test/v1",
            }
        )
    )

    conteudo = destino.read_text(encoding="utf-8")
    assert "modelo-teste" in conteudo
    assert "duracao=10ms" in conteudo
    # Segredos/endpoint jamais chegam ao arquivo.
    assert "sk-NAO-DEVE-APARECER-9999" not in conteudo
    assert "servidor-secreto.test" not in conteudo

    # Limpa handlers para não vazar estado entre testes.
    for manipulador in list(logs.LOG.handlers):
        logs.LOG.removeHandler(manipulador)
        manipulador.close()
