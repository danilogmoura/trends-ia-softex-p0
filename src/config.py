"""Carregamento da configuração sensível do acesso ao LLM.

Responsabilidade única: ler base URL, chave e modelo a partir de variáveis de
ambiente (.env fora do versionamento) e falhar de forma controlada quando algo
obrigatório estiver ausente — sem jamais expor o valor de um segredo.
"""


def carregar_config() -> dict:
    """Carrega a configuração do LLM a partir do ambiente.

    Variáveis mínimas (nomes definidos na decisão 0.6):
      - ``LLM_BASE_URL``
      - ``LLM_API_KEY``
      - ``LLM_MODEL``

    Regras (a implementar nos itens 4+):
      - Credencial ausente → erro claro indicando a variável faltante, sem
        imprimir nenhum valor sensível.

    Retorna um dicionário com os parâmetros de conexão.
    """
    # NotImplementedError é subclasse de RuntimeError, o que faria os testes do
    # item 2 passarem por acidente. Um tipo neutro garante estado 'vermelho' real.
    raise AssertionError("carregar_config será implementada no item 4 (feat)")
