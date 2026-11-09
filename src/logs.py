"""Registros simples de execução (Nível Avançado — item 2).

Fronteira única de *logging* do app, escrita para ajudar a compreender o ciclo
(entrada → config → chamada → resposta) **sem** armazenar nada proibido pelo
enunciado: chaves, tokens, credenciais, dados pessoais ou conteúdo sensível
desnecessário. Por isso:

- os registros vão para um **arquivo de log local** (por padrão ``logs/execucao.log``),
  que fica **fora do versionamento** (``.gitignore`` já cobre ``logs/`` e ``*.log``).
  Assim o terminal exibe apenas a análise pedida, sem misturar diagnóstico;
- o caminho é ajustável por configuração externa (``LLM_LOG_FILE``), coerente com
  o item 1 — sem tocar no núcleo da aplicação;
- nunca se loga a entrada do usuário nem o texto devolvido pelo modelo — apenas
  métricas (duração, tamanho, contagem de mensagens) e o nome do modelo;
- :func:`configuracao_para_log` é a função-guarida que recorta um dict de config
  para o mínimo inofensivo, impedindo que ``api_key``/``base_url`` vazem por
  descuido em qualquer chamada de log futura.

Se o arquivo não puder ser criado (permissão, caminho inválido), o logger cai em
stderr com um aviso pontual — registro é diagnóstico e nunca derruba a análise.
"""

import logging
import os
import sys

# Único logger do app. Toda instrumentação usa este canal, então controlar o
# nível aqui controla a verbosidade da execução inteira.
LOG = logging.getLogger("p0")

_NIVEIS_VALIDOS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

# Caminho padrão do arquivo de log local (gitignored). Ajustável por LLM_LOG_FILE.
_CAMINHO_PADRAO = os.path.join("logs", "execucao.log")


def _resolver_caminho(caminho: str | None) -> str:
    """Define onde o log será escrito.

    Ordem de precedência: argumento explícito → variável de ambiente
    ``LLM_LOG_FILE`` → :data:`_CAMINHO_PADRAO`. Retorna sempre uma string
    (nunca ``None``); vazio no env é tratado como ausente.
    """
    if caminho:
        return caminho
    bruto = (os.environ.get("LLM_LOG_FILE") or "").strip()
    return bruto or _CAMINHO_PADRAO


def configurar(nivel: str | None = None, caminho: str | None = None) -> None:
    """Instala o handler de arquivo uma única vez e aplica o nível efetivo.

    Idempotente: se já houver handler nosso, não duplica. Chamado no início de
    ``main()`` antes de qualquer registro. ``nivel`` vem da config (ou do
    ambiente via :func:`nivel_efetivo`); ausente, usa INFO. ``caminho`` resolve o
    destino (:func:`_resolver_caminho`); se o arquivo não puder ser aberto, emite
    aviso no stderr e mantém o comportamento anterior (stderr) para não perder
    diagnóstico.
    """
    alvo = (nivel or nivel_efetivo()).upper()
    LOG.setLevel(getattr(logging, alvo, logging.INFO))
    if not LOG.handlers:
        destino = _resolver_caminho(caminho)
        manipulador: logging.Handler
        try:
            diretorio = os.path.dirname(destino)
            if diretorio:
                os.makedirs(diretorio, exist_ok=True)
            manipulador = logging.FileHandler(destino, encoding="utf-8")
        except OSError as erro:
            print(
                f"[log] Não foi possível abrir o arquivo de log ({type(erro).__name__}); "
                "usando stderr. Verifique LLM_LOG_FILE.",
                file=sys.stderr,
            )
            manipulador = logging.StreamHandler(sys.stderr)
        manipulador.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        LOG.addHandler(manipulador)
    # Sem propagar para o root: evita double-print quando outra lib configura logging.
    LOG.propagate = False


def nivel_efetivo() -> str:
    """Resolve o nível de log do ambiente, tolerante a valor inválido.

    Lê ``LLM_LOG_LEVEL``. Nome válido (case-insensitive) é normalizado para
    maiúsculas. Valor ausente vira ``INFO``. Valor presente porém desconhecido
    **não derruba** o app: emite um aviso pontual no stderr citando só o nome da
    variável (nunca o valor cru) e segue com ``INFO``.
    """
    import os

    bruto = (os.environ.get("LLM_LOG_LEVEL") or "").strip()
    if not bruto:
        return "INFO"
    candidato = bruto.upper()
    if candidato in _NIVEIS_VALIDOS:
        return candidato
    print(
        "[log] A variável LLM_LOG_LEVEL tem valor desconhecido; usando INFO. "
        "Níveis aceitos: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
        file=sys.stderr,
    )
    return "INFO"


def resumo_de_chamada(
    *, model: str, duracao_ms: int, n_mensagens: int, chars_resposta: int
) -> str:
    """Monta a frase de diagnóstico de uma chamada ao LLM.

    Contém apenas métricas e o nome do modelo. Não recebe — e portanto não pode
    vazar — a entrada do usuário nem o corpo da resposta.
    """
    return (
        f"chamada concluída: model={model} duracao={duracao_ms}ms "
        f"mensagens={n_mensagens} resposta_chars={chars_resposta}"
    )


def configuracao_para_log(config: dict) -> str:
    """Recorta a config para uma string segura de diagnóstico.

    Expõe somente o modelo e os parâmetros de geração opcionais (não sensíveis).
    ``api_key`` e ``base_url`` ficam de fora por construção — a função simplesmente
    não os lê, então nenhuma chamada futura consegue despejá-los num log.
    """
    partes = [f"model={config.get('model', '?')}"]
    for chave in ("max_tokens", "temperature", "timeout"):
        if chave in config:
            partes.append(f"{chave}={config[chave]}")
    return " ".join(partes)
