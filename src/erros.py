"""Camada de tratamento de erros do acesso ao LLM (Nível Intermediário).

Fronteira que concentra as responsabilidades ligadas a falha, hoje ausentes dos
módulos que deixavam a exceção crua da biblioteca ``openai`` vazar até o usuário:

- :class:`ErroDeLlm` e subclasses — exceções de domínio, cada uma com mensagem
  humana e sem qualquer segredo (nunca ecoam chave, endpoint real ou stack trace);
- :func:`chamar_llm` — ponto único de contato com a API; traduz as exceções
  técnicas em exceções de domínio (cenários 3, 4 e 5 da matriz de erros) e extrai
  o texto por :func:`validar_resposta`;
- :func:`validar_resposta` — rejeita corpo vazio ou estrutura inesperada antes de
  seguir para processamento/apresentação (cenário 6);
- :func:`validar_configuracao` — confere o *formato* dos valores carregados, não
  só a presença (cenário 1), levantando :class:`ErroDeConfiguracao`.

Códigos de saída **não** variam por classe (decisão 0.14): toda a família
:class:`ErroDeLlm` é tratada igual pelo ``app``, e a distinção vive só na frase
transportada pela exceção.
"""

from urllib.parse import urlparse

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)


class ErroDeLlm(RuntimeError):
    """Base de todos os erros de domínio do acesso ao LLM.

    Sempre transporta uma mensagem legível para o usuário e jamais contém
    credencial, endpoint real ou rastro técnico.
    """


class ErroDeConfiguracao(ErroDeLlm):
    """Cenário 1 — configuração presente porém inválida (ex.: base_url malformada)."""


class ErroDeAutenticacao(ErroDeLlm):
    """Cenário 3 — credencial inválida (a API recusa a autenticação)."""


class ErroIndisponibilidade(ErroDeLlm):
    """Cenário 4 — serviço indisponível ou conexão recusada."""


class ErroTimeout(ErroDeLlm):
    """Cenário 5 — estouro de prazo.

    Deliberadamente **não** herda de :class:`ErroIndisponibilidade`: timeout é
    um diagnóstico distinto de "servidor fora do ar" e deve poder ser tratado à
    parte pelo chamador.
    """


class ErroDeResposta(ErroDeLlm):
    """Cenário 6 — resposta vazia ou em formato inesperado."""


def chamar_llm(cliente: OpenAI, config: dict, mensagens: list[dict]) -> str:
    """Ponto único de contato com a API, com tradução de exceções.

    ``cliente`` é um objeto compatível com o cliente OpenAI (em produção, o
    próprio; nos testes, um fake que lança as exceções reais da biblioteca).
    Retorna o texto bruto da resposta ou levanta uma exceção de domínio clara —
    nunca propaga a exceção técnica crua nem expõe a credencial usada.

    A ordem dos ``except`` importa: :class:`APITimeoutError` é subclasse de
    :class:`APIConnectionError`, então precisa ser capturada **antes** para que o
    timeout seja distinguido de uma queda de conexão comum (cenário 5 ≠ 4).
    """
    try:
        resposta = cliente.chat.completions.create(
            model=config["model"],
            messages=mensagens,
        )
    except AuthenticationError:
        raise ErroDeAutenticacao(
            "A credencial do LLM foi recusada (autenticação inválida). Confira "
            "LLM_API_KEY no seu ambiente (.env). Verifique também se a chave não "
            "expirou ou foi revogada pelo provedor."
        ) from None
    except APITimeoutError:
        raise ErroTimeout(
            "O LLM demorou demais para responder (tempo esgotado). Tente novamente "
            "em instantes; se persistir, reduza o tamanho da lista de ingredientes."
        ) from None
    except APIConnectionError:
        raise ErroIndisponibilidade(
            "Não foi possível falar com o LLM — serviço indisponível ou conexão "
            "recusada. Tente mais tarde e confira sua conexão de rede."
        ) from None
    except APIStatusError as erro:
        # Qualquer outra resposta HTTP de erro (4xx/5xx) que não seja auth:
        # 5xx é queda do serviço; 4xx é problema na requisição. Traduzimos sem
        # ecoar corpo, endpoint ou cabeçalhos.
        status = erro.status_code
        if status >= 500:
            raise ErroIndisponibilidade(
                f"O LLM respondeu com erro do servidor (HTTP {status}). Tente mais "
                "tarde — o problema está do lado do serviço, não na sua entrada."
            ) from None
        raise ErroDeLlm(
            f"O LLM recusou a solicitação (HTTP {status}). Verifique a configuração "
            "de acesso (modelo e parâmetros) e tente novamente."
        ) from None

    return validar_resposta(resposta)


def validar_resposta(resposta: object) -> str:
    """Extrai o texto utilizável de uma resposta da API (cenário 6).

    Aceita tanto o objeto retornado pela lib ``openai`` (com ``choices``) quanto
    um corpo já reduzido a string (casos de teste). Corpo ausente, vazio ou em
    estrutura inesperada vira :class:`ErroDeResposta` com mensagem clara, em vez
    de passar silencioso para a apresentação.
    """
    conteudo: object = resposta
    if hasattr(resposta, "choices"):
        choices = getattr(resposta, "choices") or []
        escolha = choices[0] if choices else None
        mensagem = getattr(escolha, "message", None) if escolha is not None else None
        conteudo = getattr(mensagem, "content", None) if mensagem is not None else None

    if conteudo is None:
        raise ErroDeResposta(
            "O LLM não retornou conteúdo (resposta vazia ou em formato "
            "inesperado). Tente novamente; se persistir, revise a entrada."
        )
    if not isinstance(conteudo, str):
        raise ErroDeResposta(
            "A resposta do LLM veio num formato inesperado (não é texto). "
            "Tente novamente."
        )
    if conteudo.strip() == "":
        raise ErroDeResposta(
            "O LLM respondeu, mas o conteúdo veio vazio. Tente novamente com uma "
            "lista de ingredientes um pouco diferente."
        )
    return conteudo


def validar_configuracao(config: dict) -> dict:
    """Valida o *formato* dos valores de configuração (cenário 1).

    Além da presença (já garantida em ``config.carregar_config``), verifica se
    ``base_url`` tem forma de URL absoluta válida, levantando
    :class:`ErroDeConfiguracao` que cita o nome da variável problemática
    (``LLM_BASE_URL``) **sem jamais expor seu valor**.
    """
    base_url = config.get("base_url", "")
    try:
        localizador = urlparse(base_url)
        valido = localizador.scheme in ("http", "https") and bool(localizador.netloc)
    except ValueError:
        valido = False
    if not valido:
        raise ErroDeConfiguracao(
            "A variável LLM_BASE_URL não contém uma URL válida. Use o formato "
            "completo, por exemplo https://servidor/v1 . (Consulte o .env.example.)"
        )
    return config

