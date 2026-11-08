"""Carregamento da configuração sensível do acesso ao LLM.

Responsabilidade única: ler base URL, chave e modelo a partir de variáveis de
ambiente (.env fora do versionamento) e falhar de forma controlada quando algo
obrigatório estiver ausente — sem jamais expor o valor de um segredo.
"""

import os

from dotenv import load_dotenv

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

    return {
        "base_url": os.environ["LLM_BASE_URL"].strip(),
        "api_key": os.environ["LLM_API_KEY"].strip(),
        "model": os.environ["LLM_MODEL"].strip(),
    }

