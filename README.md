# P0 — Primeiro fluxo com LLM · Decodificador de Rótulos de Ingredientes

Aplicação em **Python** que recebe a lista de ingredientes de um produto
industrializado (colada no terminal) e usa **um único LLM** para devolver uma
análise acessível ao consumidor: painel de alertas de restrição alimentar +
decodificação funcional dos aditivos. É o ciclo de 4 passos do Nível Básico:
receber entrada → preparar e enviar ao modelo → processar a resposta → apresentar
o resultado.

---

## O problema

Listas de ingredientes de rótulos vêm cheias de termos técnicos, códigos **INS** e
subprodutos que **mascaram alérgenos**. Quem tem restrição alimentar precisa
interpretar isso rápido, mas nem sempre sabe que *malte de cevada* contém glúten ou
que *caseinato* é derivado de leite.

**Quem tem a necessidade:** consumidor brasileiro com restrição alimentar
(intolerância à lactose, doença celíaca / restrição a glúten — Lei 10.674/2003;
alergia a leite ou soja — RDC 26/2015 Anvisa) ou quem só quer entender o que come
sem formação em química de alimentos.

**Entrada:** um bloco de texto colado no terminal — a lista de ingredientes copiada
da embalagem, com o ruído real dela (quebras de linha irregulares, vírgulas fora de
ordem, parênteses aninhados, abreviações).

**Saída:** texto estruturado em duas partes:

1. **Painel de alérgenos e restrições** — cada termo detectado com seu impacto em
   uma linha (glúten, lactose, soja, corantes críticos como Tartrazina INS 102 e
   Carmim INS 120), citando o termo exato do rótulo que motivou o alerta.
2. **Tabela de aditivos** — `Código INS | Ingrediente no Rótulo | Função Tecnológica
   | O que é / Descrição`.

## Por que usar um LLM

Uma busca determinística (regex/dicionário) falha nos quatro pontos que formam o
núcleo do problema:

- **Sinonímia/polimorfismo:** o mesmo aditivo aparece como nome químico (*ácido
  fosfórico*), classe genérica (*acidulante*), código normativo (*INS 338*) ou nome
  comercial — enumerar todas as variantes é inviável.
- **Alérgenos ocultos em subprodutos:** regex por "leite" não captura *soro de leite
  em pó*, *caseinato de cálcio*; regex por "glúten" não captura *malte de cevada*.
- **Semântica de risco calibrada:** o modelo distingue corante natural inócuo
  (*cúrcuma*) de sintético com reatividade cruzada (*tartrazina*) — alerta preciso,
  sem alarmismo.
- **Tolerância a ruído de entrada:** texto de embalagem quebra parsers sintáticos; o
  LLM interpreta mesmo com formatação irregular.

## Limite de escopo (importante)

A ferramenta é um decodificador **informacional**. Ela **não** emite conselho
médico, prescrição alimentar nem avaliação de segurança individual. A decisão final
sobre consumir ou não um produto **permanece humana** (e, em caso de dúvida, de um
profissional de saúde). Um aviso legal curto é impresso no topo de toda análise.

---

## Requisitos

- **Python 3.12 ou superior.** A versão usada no desenvolvimento e documentada aqui
  é a **3.12.3**; o projeto também foi validado em **3.13** e **3.14.7**, nos quais
  todas as dependências instalam e os testes passam. O enunciado não fixa uma
  versão mínima — exige apenas que a versão seja declarada (esta seção).
- **pip** (já vem com o Python).
- Acesso a um serviço de LLM que exponha **API compatível com OpenAI**, com uma
  chave de acesso. Configure-o conforme a documentação do serviço escolhido e as
  orientações institucionais, quando aplicáveis.

As dependências estão declaradas em [`requirements.txt`](requirements.txt):

| Pacote | Para quê |
| --- | --- |
| `openai` | cliente da API do LLM (endpoint compatível com OpenAI) |
| `python-dotenv` | carregar `.env` (configuração sensível fora do código) |
| `pytest` | suíte de testes local |

## Instalação

Siga os comandos abaixo **na ordem**, a partir da pasta onde quer clonar o projeto.

**1. Clonar o repositório**

```bash
git clone <URL-DO-SEU-REPOSITORIO> trends-ia-softex-p0
cd trends-ia-softex-p0
```

**2. Criar um ambiente virtual** (isolado do Python do sistema)

Comando único, vale para qualquer versão 3.12+ e para Linux/macOS/Windows:

```bash
python -m venv .venv
```

> Se o seu sistema não reconhece `python` (comum no Windows), troque por `py`:
> `py -m venv .venv`. Se tiver **várias** versões de Python instaladas e quiser
> fixar uma delas, use o nome da versão — ex.: `python3.14 -m venv .venv`
> (Linux/macOS) ou `py -3.14 -m venv .venv` (Windows). Qualquer 3.12+ funciona.

**3. Ativar o ambiente virtual**

Linux / macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

> Quando ativado, o prompt passa a mostrar `(.venv)` no início da linha.

**4. Instalar as dependências exatamente nas versões declaradas**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para conferir que tudo foi instalado:

```bash
python -m pip freeze
```

## Configuração

O programa **não** tem nenhuma credencial embutida. Ele lê três variáveis de
ambiente. Copie o modelo e preencha:

```bash
cp .env.example .env
```

Edite o `.env` criado e defina os **valores reais** fornecidos pelo seu serviço de
LLM:

| Variável | O que colocar |
| --- | --- |
| `LLM_BASE_URL` | URL base do endpoint compatível com OpenAI (formato `https://.../v1`) |
| `LLM_API_KEY` | sua chave de acesso ao serviço |
| `LLM_MODEL` | o identificador exato do modelo a usar |

### Parâmetros de geração (opcionais)

Além das três chaves obrigatórias, é possível ajustar o comportamento da chamada
**sem editar o código**, definindo variáveis opcionais no `.env`. Se você não as
preencher, o programa simplesmente não as envia e o provedor aplica seus próprios
padrões.

| Variável | Efeito | Formato aceito |
| --- | --- | --- |
| `LLM_MAX_TOKENS` | limite máximo de tokens da resposta | inteiro positivo (ex.: `512`) |
| `LLM_TEMPERATURE` | criatividade da amostragem (menos = mais determinístico) | número entre `0` e `2` (ex.: `0.3`) |
| `LLM_TIMEOUT` | tempo máximo de espera pela resposta, em segundos | número maior que zero (ex.: `30`) |

Um valor presente porém inválido faz o programa falhar com mensagem clara citando
**apenas o nome** da variável e a faixa esperada (código de saída `2`) — nunca um
segredo nem stack trace.

Segurança:

- O arquivo `.env` está no [`.gitignore`](.gitignore) e **nunca deve ser enviado**
  ao repositório (ele é público). Só o `.env.example`, com placeholders, é
  versionado.
- Não cole a chave em logs, prints, vídeos ou issues.
- Se faltar qualquer uma das três variáveis, o programa falha com mensagem clara
  indicando **apenas o nome** ausente — jamais um valor.

## Execução

Com o `.venv` ativado e o `.env` preenchido:

```bash
python -m src.app
```

O programa pede a lista de ingredientes. Cole o texto e finalize com **uma linha em
branco + Enter**:

```
Cole a lista de ingredientes do rótulo.
Quando terminar, deixe uma linha em branco e pressione Enter.
> FARINHA DE TRIGO ENRIQUECIDA COM FERRO E ÁCIDO FÓLICO, AÇÚCAR, ÓLEO DE SOJA,
> SAL, FERMENTO BIOLÓGICO, EMULSIFICANTE MONOGLICERÍDEOS DE ÁCIDOS GRAXOS,
> CONSERVADOR PROPIONATO DE CÁLCIO, CORANTE TARTRAZINA, AROMATIZANTE.
>
```

Também dá para enviar direto por *pipe* (útil para testar sem digitar):

```bash
echo "farinha de trigo, açúcar, óleo de soja, sal, corante tartrazina" | python -m src.app
```

## Exemplo de saída

Formato real gerado pela aplicação (resumo ilustrativo de uma entrada com glúten,
soja e corante crítico):

```text
==================== ANÁLISE DO RÓTULO ====================

> Análise informativa. Não substitui avaliação médica/nutricional. Decisão final
é sua.

[CONTÉM: glúten (trigo), soja | ATENÇÃO: corante tartrazina (INS 102)]

SEÇÃO 1 — PAINEL DE ALÉRGICOS E RESTRIÇÕES
- farinha de trigo: contém glúten (Lei 10.674/2003); restrição para
  celíacos/sensibilidade ao glúten.
- óleo de soja: alérgeno de soja (RDC 26/2015 Anvisa); restrição para alergia à
soja.
- Corantes sintéticos/críticos: Tartrazina (INS 102).

SEÇÃO 2 — TABELA DE ADITIVOS
| Código INS | Ingrediente no Rótulo | Função Tecnológica | O que é / Descrição
|
|---|---|---|---|
| 102 | corante tartrazina | Corante | Corante sintético amarelo usado para dar
coloração. |
```

> Os termos detectados e as descrições variam conforme o modelo configurado; o
> formato estrutural (aviso legal → resumo → painel → tabela) é o contrato fixo da
> aplicação.

## Testes

A suíte roda **offline**, sem chamar o LLM (testa apenas lógica determinística de
entrada e configuração):

```bash
python -m pytest
```

Saída esperada:

```text
............                                      [100%]
12 passed
```

Cobertura atual:

- `tests/test_entrada.py` — bloqueio de entrada vazia/só espaços, normalização e
  limite de tamanho.
- `tests/test_config.py` — erro claro quando falta credencial ou a base URL é
  inválida, e garantia de que a mensagem de erro **não** expõe o valor de nenhum
  segredo.
- `tests/test_rede.py` — credencial inválida, indisponibilidade e timeout, cada um
  convertido em erro próprio de leitura curta.
- `tests/test_resposta.py` — resposta vazia ou em formato inesperado rejeitada pela
  camada de tratamento.

### Testes simulados × chamada real

Conforme o enunciado exige distinguir as duas naturezas:

- **Todos os 12 testes acima são simulados** — rodam offline, sem rede. Eles usam
  um *cliente falso* que lança exatamente as exceções do serviço (`AuthenticationError`,
  `APIConnectionError`, `APITimeoutError`) e uma resposta artificial vazia/`None`,
  para provar o tratamento controlado **sem** chamar o LLM nem expor qualquer chave.
- **A chamada real ao LLM** é demonstrada à parte, executando a aplicação
  (`python -m src.app`) com um `.env` válido: é ela que prova o funcionamento do
  fluxo completo contra o serviço escolhido. Nenhum teste automatizado usa
  credencial real.

## Tratamento de erros (Nível Intermediário)

A aplicação encerra de forma controlada nos cenários previsíveis, imprimindo no
`stderr` uma frase curta — nunca um *traceback* técnico — e reaproveitando os
códigos de saída já existentes (decisão registrada no plano):

| Cenário | Prefixo no `stderr` + início da mensagem real | Saída |
| --- | --- | --- |
| Configuração ausente/incompleta | `[configuração] Configuração do LLM incompleta. Defina ... a(s) variável(is): LLM_API_KEY` | `2` |
| Base URL inválida | `[configuração] A variável LLM_BASE_URL não contém uma URL válida` | `2` |
| Credencial inválida | `[LLM] A credencial do LLM foi recusada (autenticação inválida)` | `1` |
| Indisponibilidade / falha de comunicação | `[LLM] Não foi possível falar com o LLM — serviço indisponível ou conexão recusada` | `1` |
| Timeout | `[LLM] O LLM demorou demais para responder (tempo esgotado)` | `1` |
| Resposta vazia/formato inesperado | `[LLM] O LLM não retornou conteúdo (resposta vazia ou em formato inesperado)` | `1` |
| Entrada vazia | `[entrada inválida]` com orientação para colar a lista | `1` |
| Interrupção (Ctrl+C) | `Execução interrompida pelo usuário.` | `130` |

Nenhuma dessas mensagens contém chave, token, endpoint real ou dado pessoal — só o
**nome** da variável ou uma descrição genérica do problema.

## Estrutura do repositório

```text
src/
  app.py        # ponto de entrada — orquestra os 4 passos (python -m src.app)
  entrada.py    # passo 1: captura e validação da entrada textual
  config.py     # carregamento da configuração sensível (.env), sem expor valores
  erros.py      # camada de tratamento: traduz falhas do serviço em erros legíveis
  llm.py        # passos 2–3: prepara/envia a solicitação e processa a resposta
tests/
  test_entrada.py
  test_config.py
  test_rede.py
  test_resposta.py
.env.example    # modelo das variáveis de ambiente (sem valores reais)
requirements.txt
pytest.ini
```

## Solução de problemas

| Sintoma | Causa provável | O que fazer |
| --- | --- | --- |
| `[configuração] ... variável(s): LLM_API_KEY` | `.env` ausente ou incompleto | `cp .env.example .env` e preencha as três chaves |
| `ModuleNotFoundError: openai` | venv não ativado / deps não instaladas | ative o `.venv` e rode `python -m pip install -r requirements.txt` |
| Erro de conexão/TLS ao chamar o modelo | endpoint errado, rede ou credencial inválida | confira `LLM_BASE_URL` exatamente como o serviço indica e a validade da chave |
| `(o modelo não retornou conteúdo)` | resposta vazia do serviço | verifique o modelo configurado e tente novamente |

## Limitações conhecidas

- Ferramenta **informacional**: não substitui avaliação médica/nutricional; a
  decisão final é humana.
- Depende da disponibilidade do serviço de LLM escolhido; indisponibilidade,
  timeout ou resposta vazia são sinalizados com mensagem clara, mas não há fallback
  offline.
- No Nível Intermediário os sete cenários previsíveis já são tratados de forma
  controlada (ver seção *Tratamento de erros*); permanecem fora de escopo retries
  automáticos e cache local de respostas.
- A qualidade da análise reflete o modelo configurado; resultados podem variar
  entre modelos e versões.
