"""Preparo e envio da solicitação ao LLM (compatível com API OpenAI).

Responsabilidade única: montar a mensagem (system + usuário) e chamar o único
modelo configurado, devolvendo o texto da resposta. A conexão vem sempre de
``carregar_config()`` — nada de base URL, chave ou modelo hardcoded aqui.
"""

from openai import OpenAI

# Prompt do sistema: define o papel informacional e o limite anti-diagnóstico
# (regra do projeto: decisão final permanece humana).
SYSTEM_PROMPT = (
    "Você é um decodificador de rótulos de alimentos para o consumidor brasileiro. "
    "Recebe a lista de ingredientes copiada de uma embalagem e devolve DUAS partes:\n"
    "1) PAINEL DE ALERTAS priorizando restrições alimentares comuns no Brasil "
    "(glúten/doença celíaca — Lei 10.674/2003; lactose; alergia a leite e soja — RDC "
    "26/2015 Anvisa; corantes críticos como Tartrazina INS 102 e Carmim/Cochonilha "
    "INS 120). Para cada alerta, CITE o termo exato do rótulo que o motivou, inclusive "
    "quando o alérgeno está mascarado em um subproduto (ex.: 'malte de cevada' → glúten; "
    "'caseinato', 'soro de leite' → leite/lactose).\n"
    "2) TABELA de decodificação dos aditivos: nome/código INS, o que é e para que serve "
    "no produto.\n"
    "Se não houver compostos industriais sintéticos, diga isso explicitamente, sem forçar "
    "classificação. Se o texto não for uma lista de ingredientes (ex.: instruções de "
    "preparo, erro técnico), pare e peça a correção da entrada, sem inventar análise.\n"
    "IMPORTANTE: sua saída é INFORMATIVA e culinária. Não emite conselho médico, "
    "prescrição alimentar nem avaliação de segurança individual."
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
    Nenhum valor sensível é impresso aqui; erros de conexão são propagados ao
    chamador (tratamento controlado vem no Nível Intermediário).
    """
    cliente = OpenAI(base_url=config["base_url"], api_key=config["api_key"])

    resposta = cliente.chat.completions.create(
        model=config["model"],
        messages=preparar_mensagens(entrada_validada),
    )

    # Resposta pode vir sem conteúdo (choice ausente ou message vazia); o
    # tratamento dessa ausência é validado offline no item 6. Aqui apenas
    # extraímos o texto quando presente.
    escolha = resposta.choices[0] if resposta.choices else None
    conteudo = escolha.message.content if escolha and escolha.message else None
    return conteudo or ""
