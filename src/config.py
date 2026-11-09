"""Carregamento da configuração sensível do acesso ao LLM.

Responsabilidade única: ler base URL, chave e modelo a partir de variáveis de
ambiente (.env fora do versionamento) e falhar de forma controlada quando algo
obrigatório estiver ausente — sem jamais expor o valor de um segredo.
"""

import os

from dotenv import load_dotenv

from . import erros, logs

# Nomes das variáveis obrigatórias (decisão 0.6). Os VALORES nunca são lidos
# para log nem incluídos em mensagens de erro — apenas os NOMES faltantes.
VARIAVEIS_OBRIGATORIAS = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")


class ConfiguracaoAusenteError(RuntimeError):
    """Configuração obrigatória ausente ou vazia.

    A mensagem contém apenas os NOMES das variáveis faltantes — nunca valores.
    """


def carregar_config(*, carregar_arquivo: bool = True) -> dict:
    """Carrega a configuração do LLM a partir do ambiente.

    Lê ``LLM_BASE_URL``, ``LLM_API_KEY`` e ``LLM_MODEL``. Se qualquer uma estiver
    ausente ou vazia, levanta :class:`ConfiguracaoAusenteError` indicando o nome
    da variável faltante, sem imprimir nenhum valor sensível.

    ``carregar_arquivo`` controla se o ``.env`` local é lido do disco. Em runtime
    normal é ``True``; em testes passa ``False`` para observar apenas o ambiente
    já preparado (sem o ``.env`` real sobrescrever o cenário simulado).

    Retorna um dicionário com os parâmetros de conexão.
    """
    # Carrega o .env local (se existir) sem sobrescrever variáveis já definidas
    # no ambiente real. Desligável para permitir testes determinísticos.
    if carregar_arquivo:
        load_dotenv()

    faltantes = [
        nome for nome in VARIAVEIS_OBRIGATORIAS
        if not (os.environ.get(nome) or "").strip()
    ]
    if faltantes:
        raise ConfiguracaoAusenteError(
            "Configuração do LLM incompleta. Defina no ambiente (ou no .env) "
            f"a(s) variável(is): {', '.join(faltantes)}. "
            "Consulte o .env.example para os nomes esperados."
        )

    return erros.validar_configuracao(
        {
            "base_url": os.environ["LLM_BASE_URL"].strip(),
            "api_key": os.environ["LLM_API_KEY"].strip(),
            "model": os.environ["LLM_MODEL"].strip(),
        }
    ) | _ler_parametros_geracao() | _ler_config_logs()


def _ler_config_logs() -> dict:
    """Lê as variáveis de registro (Avançado — item 2) e normaliza para a config.

    Trata duas variáveis **opcionais** e **tolerantes**, ambas de diagnóstico:

    - ``LLM_LOG_LEVEL``: ausente → sem chave (app usa INFO); válido → injeta
      ``log_level`` maiúsculo; desconhecido → **não derruba** a app, retorna vazio
      e :func:`src.logs.nivel_efetivo` avisa no stderr ao configurar o logger.
    - ``LLM_LOG_FILE``: ausente/vazio → sem chave (app usa o padrão
      ``logs/execucao.log``); presente → injeta ``log_file`` com o caminho tal
      como dado. Não há validação de conteúdo: é só um caminho, e um caminho
      inválido é tratado por :func:`src.logs.configurar` (fallback stderr).

    Coerente com o Intermediário: um erro de digitação em configuração de log
    não impede o fluxo principal nem despeja stack trace.
    """
    resultado: dict = {}

    nivel_bruto = (os.environ.get("LLM_LOG_LEVEL") or "").strip()
    if nivel_bruto:
        candidato = nivel_bruto.upper()
        if candidato in logs._NIVEIS_VALIDOS:
            resultado["log_level"] = candidato

    arquivo_bruto = (os.environ.get("LLM_LOG_FILE") or "").strip()
    if arquivo_bruto:
        resultado["log_file"] = arquivo_bruto

    return resultado


def _ler_parametros_geracao() -> dict:
    """Lê do ambiente os parâmetros de geração opcionais (Avançado — item 1).

    Coleta apenas as variáveis presentes (``LLM_MAX_TOKENS``, ``LLM_TEMPERATURE``,
    ``LLM_TIMEOUT``) e delega conversão/validação a
    :func:`src.erros.validar_parametros_geracao`. Ausentes, retornam vazio e o
    app segue com os padrões do provedor — nada é injetado na requisição.
    """
    nomes = [nome for nome, *_ in erros._PARAMETROS_OPCIONAIS.values()]
    valores_env = {
        nome: os.environ[nome] for nome in nomes if (os.environ.get(nome) or "").strip()
    }
    return erros.validar_parametros_geracao(valores_env)

