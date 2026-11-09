"""Preparo, envio e processamento da solicitação ao LLM (API compatível com OpenAI).

Responsabilidades (itens 4–5 do Nível Básico): montar a mensagem (system + usuário),
chamar o único modelo configurado e **processar** o texto devolvido, normalizando
espaços e quebras irregulares antes da apresentação. A conexão vem sempre de
``carregar_config()`` — nada de base URL, chave ou modelo hardcoded aqui.
"""

import re
import textwrap

from openai import OpenAI

from . import erros

# Prompt do sistema: define o papel informacional, o contrato de saída concisa
# para terminal (decisão 0.9) e o limite anti-diagnóstico (decisão final humana).
SYSTEM_PROMPT = (
    "Você decodifica a lista de ingredientes de um rótulo de alimento para o consumidor "
    "brasileiro. Responda SEMPRE no formato abaixo, direto ao ponto, otimizado para "
    "leitura em terminal.\n\n"
    "PROIBIDO: saudação, introdução, despedida, comentários sobre a tarefa ou qualquer "
    "conversação fora da estrutura. PROIBIDO: parágrafos didáticos explicando noções "
    "óbvias (o que é glúten, o que é trigo, o que é celíaco). Cada linha deve trazer só "
    "o termo detectado e seu impacto direto.\n\n"
    "VALIDAÇÃO: se o texto NÃO for uma lista de ingredientes (ex.: instruções de preparo, "
    "texto aleatório, erro técnico), interrompa imediatamente devolvendo apenas esta "
    "linha, sem inventar análise:\n"
    "ERRO: A entrada não é uma lista de ingredientes. Cole apenas os ingredientes do rótulo.\n\n"
    "Se for uma lista válida, produza exatamente estas partes, nesta ordem:\n\n"
    "1. AVISO LEGAL — uma linha em bloco de citação:\n"
    "> Análise informativa. Não substitui avaliação médica/nutricional. Decisão final é sua.\n\n"
    "2. RESUMO — uma única linha no padrão:\n"
    "[CONTÉM: <alérgenos/restricões presentes, separados por vírgula> | ATENÇÃO: <pontos de "
    "atenção, ex.: corante crítico>]\n"
    "Use 'nenhum' quando não houver itens naquele lado.\n\n"
    "3. SEÇÃO 1 — PAINEL DE ALÉRGICOS E RESTRIÇÕES\n"
    "Bullets enxutos; cada um traz APENAS o termo do rótulo e o impacto em uma linha, no "
    "formato `- <termo exato do rótulo>: <impacto/restrição>`. Cubra as restrições comuns "
    "no Brasil citando a base legal quando aplicável (glúten — Lei 10.674/2003; leite e "
    "soja — RDC 26/2015 Anvisa; lactose). Considere alérgeno mascarado em subproduto "
    "(ex.: 'malte de cevada' → glúten; 'caseinato'/'soro de leite' → leite/lactose). "
    "Inclua um subtópico curto `- Corantes sintéticos/críticos:` listando os presentes "
    "(ex.: Tartrazina INS 102, Carmim/Cochonilha INS 120) e, se houver, outros pontos de "
    "atenção (ex.: gordura hidrogenada/trans, nitrito). Se nada se aplicar, escreva "
    "`- Nenhum alérgeno declarado na lista.`\n\n"
    "4. SEÇÃO 2 — TABELA DE ADITIVOS\n"
    "Tabela Markdown com as colunas fixas:\n"
    "| Código INS | Ingrediente no Rótulo | Função Tecnológica | O que é / Descrição |\n"
    "Uma linha por aditivo; descrição em uma frase curta. Se não houver aditivo com código "
    "INS, escreva explicitamente: `Nenhum aditivo com código INS identificado.`\n"
)


def preparar_mensagens(entrada_validada: str) -> list[dict]:
    """Monta a lista de mensagens no formato aceito pela API compatível com OpenAI."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": entrada_validada},
    ]


def analisar_ingredientes(entrada_validada: str, config: dict) -> str:
    """Envia a solicitação ao LLM configurado e retorna o texto da resposta.

    ``config`` vem de :func:`src.config.carregar_config` (base_url, api_key, model).
    Nenhum valor sensível é impresso aqui. O contato com a API e a tradução de
    falhas ficam na camada :mod:`src.erros` (Nível Intermediário): este módulo só
    monta o cliente e delega — as exceções técnicas da lib ``openai`` nunca vazam
    para o chamador, que recebe sempre uma :class:`src.erros.ErroDeLlm` legível.
    """
    cliente = OpenAI(base_url=config["base_url"], api_key=config["api_key"])
    return erros.chamar_llm(cliente, config, preparar_mensagens(entrada_validada))


# Largura máxima de coluna para o texto do terminal (decisão 0.9). Evita que o
# modelo estenda linhas muito longas, que quebram de forma ilegível no console.
LARGURA_TERMINAL = 88


def _envolver_linha(linha: str, largura: int) -> list[str]:
    """Quebra uma linha longa em várias, respeitando a margem original.

    Linhas de tabela Markdown (começam com ``|``), blocos de citação (``>``) e
    itens de lista recebem recuo pendente coerente; nada é cortado — só envolvido.
    """
    if len(linha) <= largura:
        return [linha]
    conteudo = linha.lstrip()
    margem = linha[: len(linha) - len(conteudo)]
    # Tabelas e citações não se beneficiam de quebra no meio: mantém como está,
    # truncando visualmente apenas por largura seria perder dado — então preserva.
    if conteudo.startswith("|") or conteudo.startswith(">"):
        return [linha]
    prefixo = ""
    if conteudo.startswith("- "):
        prefixo, conteudo = "- ", conteudo[2:]
    recuo = margem + prefixo
    envolvido = textwrap.wrap(
        conteudo,
        width=max(largura - len(recuo), 20),
        initial_indent=recuo,
        subsequent_indent=margem + "  ",
    )
    return envolvido or [linha]


def processar_resposta(resposta_crua: str) -> str:
    """Passo 3 do ciclo — processa o texto devolvido pelo modelo.

    Normaliza apenas a *forma* do texto: remove espaços nas bordas, reduz
    sequências de três ou mais quebras de linha (comum em respostas Markdown)
    a no máximo duas e envolve linhas longas na largura do terminal
    (decisão 0.9), sem cortar conteúdo. Não interpreta nem reorganiza o que o
    modelo escreveu — a decodificação já vem pronta dele.

    O tratamento de resposta **ausente** ou em formato inesperado é coberto nos
    níveis Intermediário/Avançado (decisão 0.10); aqui assumimos uma string
    (possivelmente vazia) e apenas normalizamos sua forma.
    """
    texto = resposta_crua.strip()
    # \n{3,} -> \n\n : colapsa blocos de linhas em branco excessivos.
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    linhas: list[str] = []
    for linha in texto.splitlines():
        linhas.extend(_envolver_linha(linha.rstrip(), LARGURA_TERMINAL))
    return "\n".join(linhas)
