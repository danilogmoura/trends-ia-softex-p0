# PLANO P0 — Primeiro fluxo com LLM

Planejamento de execução do projeto em três marcos sucessivos do **mesmo** código
(`BÁSICO` → `INTERMEDIÁRIO` → `AVANÇADO`). Regras e checklists obrigatórios ficam em
`AGENTS.md` (fonte: enunciado oficial). Este arquivo define **ordem, calendário e
onde os testes entram em cada commit**.

Doutrina de teste: todo requisito determinístico tem teste escrito **antes** do
código; comportamento observado empiricamente (formato real da resposta do LLM)
ganha mock **depois** da primeira chamada real. Testes viajam dentro do commit da
feature correspondente — nunca como fase separada.

Calendário oficial: início 03/11/2026 · entrega única no Moodle até **06/12/2026**.
Duração prevista do P0: 4–5 semanas.

---

## Fase 0 — Decisões do aluno (antes de qualquer código)

- [x] 0.1 Problema descrito em uma frase (quem / o que entra / o que sai) → preenchido abaixo.
- [x] 0.2 Justificativa de por que um LLM (e por que regra fixa não basta) → registrada abaixo.
- [x] 0.3 Registro inicial do repositório no Moodle → link enviado na atividade. Repositório
  público criado no início do projeto. Manter o **mesmo** repositório até a entrega final.
- [ ] 0.4 Acesso ao LLM disponível (provedor conforme orientação do curso) → confirmar antes do
  item 4 do Básico. Risco mapeado: sem acesso comprovado, as fases viram apenas simuladas.
- [x] 0.5 Decisão: **provedor institucional (Devel)**. Consequências fixas: base URL, chave e nome
  do modelo vêm **somente** de configuração externa (`.env`, fora do versionamento); nada hardcoded;
  `.env.example` traz apenas nomes de variáveis sem valor. Restrição permanente: endpoint, hostname
  e modelo exato **não** aparecem em código, README, `.env.example`, logs, relatório ou vídeo
  (repositório público). Registrar no relatório que o provedor é o institucional, sem dados restritos.
- [x] 0.6 Interface de acesso confirmada: o serviço institucional expõe **API compatível com
  OpenAI** (`/v1/chat/completions`). Decisão: usar o client **`openai`** oficial apontando a
  `base_url` vinda de configuração — protocolo já conhecido pela banca, sem parsing manual de HTTP.
  Variáveis externas mínimas: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (+ parâmetros de geração
  no Avançado). **Nenhum valor real vai ao repositório.**
- [x] 0.7 **Desvio de nível registrado:** `.env.example` e cobertura do `.gitignore` foram
  **antecipados para o Básico** (item 8 da sequência) por motivo de segurança. Justificativa: o
  repositório é público e a exigência "credencial fora do código" já vale no Básico; deixar o
  template de configuração só para o Intermediário aumentaria a janela de erro humano (colocar a
  chave real em arquivo versionável, ou commitar `.env` antes de existir gitignore adequado).
  Consequências: o item 5 do Intermediário passa a ser **verificação de consistência**, não criação;
  o checklist Básico ganha um item além do enunciado (isso não custa nota — é proteção); e este
  desvio deve aparecer no relatório de execução como decisão técnica com critério objetivo.
- [x] 0.8 **Decisão de UX da entrada interativa (registrada 2026-11-08).** A captura pelo terminal
  aceita **múltiplas linhas** e se encerra com uma **linha em branco** (Enter numa linha vazia),
  em vez de `input()` de linha única. Motivo: rótulos reais vêm quebrados em várias linhas, e o
  ruído de formatação irregular é parte central da justificativa de usar LLM (seção *Entrada*);
  linha única descartaria a segunda metade do texto colado. Custo aceito conscientemente: quando o
  texto colado **não** termina em quebra, o usuário precisa de **um Enter extra** para sinalizar o
  fim — não há como distinguir "terminei" de "ainda vou colar mais" sem um marcador de término.
  Alternativas avaliadas e rejeitadas: Ctrl+D (EOF) — falha em terminais WSL/Windows; `input()` de
  linha única — perde entradas multi-linha. Exceção automática: quando a entrada vem por pipe ou
  redirecionamento (`< arquivo`), o programa lê tudo de uma vez, sem exigir linha em branco
  (detectado via `sys.stdin.isatty()`). Esta decisão aparece no relatório como escolha de escopo
  com trade-off documentado.
- [x] 0.9 **Decisão do contrato de saída (registrada 2026-11-08, a pedido do aluno).** O formato que o
  LLM devolve é reescrito para leitura em terminal: a versão anterior era verbosa e prolixa (parágrafos
  didáticos explicando noções óbvias, seções residuais repetidas, sem resumo rápido). Novo contrato,
  imposto por `SYSTEM_PROMPT` (`src/llm.py`) e refletido em `apresentar()` (`src/app.py`):
  1) aviso legal curto em bloco de citação; 2) resumo visual em linha única `[CONTÉM: ... | ATENÇÃO: ...]`;
  2) Seção 1 — painel de alérgenos/restrições em bullets enxutos (só termo detectado + impacto em uma
  linha), com subtópico para corantes sintéticos/críticos e outros pontos de atenção; 4) Seção 2 — tabela
  Markdown com colunas fixas `Código INS | Ingrediente no Rótulo | Função Tecnológica | O que é / Descrição`,
  com aviso explícito quando não há aditivo com INS; 5) interromper com erro se a entrada não for lista de
  ingredientes; 6) sem conversação (sem saudação/introdução/despedida). Rigor técnico e referências legais
  (Lei 10.674/2003, RDC 26/2015, códigos INS) preservados. Como o modelo ainda pode devolver texto longo,
  o processamento offline passa a **limitar a largura** da saída no terminal (wrap), sem cortar conteúdo.
- [x] 0.10 **Decisão de posicionamento do teste com mock (registrada 2026-11-08, a pedido do aluno).**
  O `test_resposta.py` (resposta ausente/vazia via integração simulada, sem rede) **sai do Nível Básico**
  e fica **somente no Avançado**, alinhado ao que o enunciado cobra literalmente: "teste de lógica local
  que não faça uma chamada real ao modelo" aparece apenas na seção Avançado (o Básico pede só enviar ao
  LLM escolhido e processar a resposta — a chamada é real). Consequências: o antigo item 6 do Básico é
  removido (Básico fecha nos itens 7 README e 8 `.env.example`); o mock já está coberto pelo item 3 do
  Avançado (`test(avancado): suíte local executável sem chamada real ao LLM`), que passa a incluir a
  resposta ausente/vazia; os testes que permanecem no Básico (`test_entrada`, `test_config`) são de
  **lógica determinística pura**, não dependem de simular rede — portanto continuam legítimos ali. Nada
  se perde: a doutrina de "testar além do cenário ideal" segue válida, só executada no nível correto.
- [x] 0.11 **Decisão de provedor do LLM durante o desenvolvimento (registrada 2026-11-08).** O serviço
  institucional previsto para o P0 apresentou instabilidade de disponibilidade nas janelas de
  desenvolvimento. Para não travar o fluxo de 4 passos nem os testes com chamada real, o `.env` local
  passou a apontar para um **provedor externo alternativo** que expõe endpoint compatível com a API
  OpenAI, no plano de uso sob demanda (custos do aluno), usando **um único modelo** por vez — conforme o
  enunciado permite substituir o institucional quando este não estiver disponível, arcando o aluno com o
  custo e sem suporte da instituição sobre o serviço externo. A troca é **apenas de configuração externa**
  (`LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`): nenhum código do núcleo muda, pois a conexão já vem toda
  de `carregar_config()`. Por restrição de segurança (repositório **público**), **não** se publica aqui —
  nem no README, `.env.example`, logs ou vídeo — o endereço, o nome comercial do provedor, o identificador
  exato do modelo nem qualquer credencial. O `.env.example` permanece com placeholders genéricos. No
  relatório final registra-se apenas que houve substituição por provedor externo compatível e o porquê
  (instabilidade do institucional), sem dados restritos. Se o serviço institucional voltar a ficar estável,
  basta reescrever as três variáveis do `.env` para retomá-lo, sem tocar em código.
- [x] 0.12 **Decisão de divisão "tratar × testar" a resposta vazia (registrada 2026-11-08, a pedido do aluno).**
  O checklist do Nível Intermediário exige *tratar* "resposta vazia ou em formato inesperado" com mensagem
  compreensível; a decisão 0.10 moveu o *teste com mock* dessa situação para o Avançado. Não há contradição:
  são dois artefatos distintos. No **Intermediário** implementa-se o **tratamento** (código que detecta corpo
  vazio/formato inesperado na chamada real e encerra com orientação legível, sem stack trace). No **Avançado**
  entra o **teste local offline** (`test_resposta.py`) que exercita esse mesmo tratamento por integração
  simulada, sem rede. Consequência: o item 4 do Intermediário cobre o tratamento de todos os seis cenários da
  matriz (incluindo resposta vazia); o item 3 do Avançado mantém o mock. Assim cada requisito de erro do
  checklist tem implementação no nível onde é cobrado e teste no nível onde o enunciado pede evidência offline.
- [x] 0.13 **Decisão de amplitude dos testes vermelhos do item 2 (registrada 2026-11-08, a pedido do aluno).**
  O título original do item 2 nomeava apenas três cenários (credencial inválida, indisponibilidade, timeout),
  mas o item 4 se compromete a deixar **verdes** os seis da matriz de erros. Para que todo teste verde tenha
  um vermelho correspondente escrito antes, o item 2 passa a cobrir os **seis** cenários, distribuídos por
  arquivo: `test_rede.py` (novo — credencial inválida, indisponibilidade, timeout, via cliente simulado que
  lança as exceções reais da lib `openai`), extensão de `test_config.py` (config malformed / variável inválida)
  e `test_resposta.py` (**apenas o tratamento de corpo vazio/formato inesperado observado numa chamada real**).
  Fronteira preservada com o Avançado: o **teste offline puramente simulado** de resposta ausente/vazia
  (`test_resposta.py` completo, sem nenhuma chamada de rede) permanece no item 3 do Avançado (decisão 0.12);
  nada de suíte mockada antecipada aqui. Justificativa do arquivo separado: falhas de rede exigem mockar o
  cliente OpenAI (infraestrutura distinta dos testes determinísticos de env var), então vão em `test_rede.py`
  em vez de misturar em `test_config.py`.
- [x] 0.14 **Decisão de códigos de saída no tratamento de erros (registrada 2026-11-08, a pedido do aluno).**
  O item 4 **não cria novos exit codes**. A família `ErroDeLlm` (autenticação, indisponibilidade, timeout,
  resposta) cai no código `1` já existente (mesmo da entrada inválida); config ausente/inválida permanece `2`;
  interrupção do usuário `130`. Justificativa: o princípio do curso pede a alternativa mais simples capaz de
  resolver com qualidade, e um CLI textual local não precisa que um script externo diferencie "timeout" de
  "auth" por número — a distinção vive na **mensagem humana** impressa no stderr (cada exceção carrega a sua
  frase), exatamente o que o checklist exige ("mensagem compreensível", sem erro técnico extenso). Mapear cada
  classe para um código próprio seria complexidade sem consequência do problema.

**Problema escolhido:** Traduzir a lista de ingredientes de um produto
industrializado — cheia de termos técnicos, códigos INS e subprodutos que mascaram
alérgenos — em uma análise acessível ao consumidor comum: painel de alertas de
restrição alimentar + decodificação funcional dos aditivos.

**Quem tem a necessidade:** Consumidor brasileiro com restrição alimentar (intolerância à
lactose — 50–70% dos adultos; doença celíaca / restrição a glúten, Lei 10.674/2003;
alergia a leite ou soja, RDC 26/2015 Anvisa) ou simplesmente quem quer entender o que
come sem precisar de formação em química de alimentos.

**Entrada:** Um bloco de texto colado no terminal — a lista de ingredientes copiada da
embalagem (com ruído real: quebras de linha irregulares, vírgulas/pontos desordenados,
parênteses aninhados, abreviações).
**Saída:** Texto estruturado em duas partes: (1) **painel de alertas prioritários**
(Glúten, Lactose, Soja, Corantes críticos — Tartrazina INS 102, Carmim INS 120),
citando o termo exato do rótulo que motivou cada alerta; (2) **tabela de decodificação
dos aditivos** (o que é e para que serve tecnicamente no produto). Saída verificável:
um avaliador humano confronta rótulo original × tabela e audita falsos negativos.

**Por que LLM:** busca determinística (regex/dicionário) falha nos quatro pontos que
formam o núcleo do problema:

- **Sinonímia/polimorfismo:** o mesmo aditivo aparece como nome químico formal (*ácido
  fosfórico*), classe genérica (*acidulante*), código normativo (*INS 338*) ou nome
  comercial — enumerar todas as variantes em dicionário estático é inviável.
- **Alérgenos ocultos em subprodutos:** regex por "leite" não captura *soro de leite em
  pó*, *caseinato de cálcio*, *lactoalbumina*; regex por "glúten" não captura *malte de
  cevada*, *triticale*, *farinha de espelta*.
- **Semântica de risco calibrada:** regex trata todo corante igual; o modelo distingue
  corante natural inócuo (*cúrcuma*, *clorofila*), de origem animal alergênico (*carmim
  de cochonilha*) e sintético com reatividade cruzada (*tartrazina*) — alerta preciso, sem alarmismo.
- **Tolerância a ruído de entrada:** texto de embalagem quebra parsers sintáticos; o LLM
  interpreta mesmo com formatação irregular.

**Limite rígido de escopo (anti-diagnóstico):** a ferramenta é decodificador
químico-culinário **informacional**. Não emite conselho médico, prescrição alimentar nem
avaliação de segurança individual — decisão final permanece humana (princípio do curso
para decisões de alto impacto em saúde).

> Risco mapeado: sem 0.1–0.2 nada avança. Sem 0.4, as fases 1–3 viram apenas
> simuladas — a chamada real é obrigatória para provar o funcionamento.

---

## Nível 1 — BÁSICO (primeiro fluxo funcional)

**Objetivo:** ciclo de 4 passos funcionando com entrada de terminal e **um** LLM real.

### Testes primeiro (falham de propósito → depois passam)

| Teste | Cenário coberto | Evidência mínima do enunciado |
| --- | --- | --- |
| `test_entrada.py` | entrada vazia/só espaços é bloqueada com orientação | "Entrada vazia" |
| `test_entrada.py` | sanitização pré-envio: texto excessivamente longo barrado por regex antes de consumir a API | "Sanitização pré-envio" |
| `test_config.py` | credencial ausente → erro claro, sem expor segredo | "Credencial ausente" |

> O teste com **mock de resposta** (ausente/vazia, sem rede) foi movido para o Avançado pela
> decisão 0.10 — o enunciado o cobra só lá. No Básico ficam apenas os testes de lógica determinística.

**Bateria de robustez do domínio** (decidir em qual nível cada uma entra; sempre que o
problema permitir, testar além do cenário ideal — falha bem investigada é evidência):

| Caso | Entrada | Critério de sucesso |
| --- | --- | --- |
| Negativo — ausência de aditivos | *"leite pasteurizado, café solúvel e canela"* | declarar explicitamente que não há compostos industriais sintéticos, sem forçar classificação |
| Alérgenos ocultos em subprodutos | rótulo com *"malte"* e *"caseinato"* | alertas de glúten e lactose disparados citando o termo original |
| Fora de escopo | mensagem de erro técnico ou receita caseira com instruções de preparo | interromper o fluxo e pedir correção da entrada, sem inventar análise |

### Decisão de layout (registrada 2026-11-08)

Pacote `src/` com responsabilidades separadas em módulos; **ponto de entrada = `src/app.py`**
(decisão do aluno). Execução documentada como `python -m src.app`. Estrutura-alvo:

```
src/
  __init__.py
  app.py       # orquestra o ciclo de 4 passos — itens 4–5  (criado no item 4)
  entrada.py   # validar_entrada()      — item 3  (implementado)
  config.py    # carregar_config()      — item 4  (implementado)
  llm.py       # preparar/enviar + processar resposta — itens 4–5  (criado no item 4)
tests/         # test_entrada, test_config (test_resposta entra no Avançado — decisão 0.10)
pytest.ini     # pythonpath=. · testpaths=tests
```

### Sequência de commits prevista

Item concluído **somente** quando: commit aprovado pelo usuário e executado **+**
evidência verificável (comando citado na coluna). Marque `- [x]` no mesmo diff que
apresenta o resultado.

- [x] 0. `docs(p0): regras do agente, plano e instruções do repositório` — `AGENTS.md`, `PLANO.md`
  e `.github/instructions/` versionados; varredura do staged diff sem cadeia de segredo.
  **Commit `fb6f7ab`** (2026-11-08): 4 arquivos, 643 inserções; varredura confirmou ausência de IP,
  hostname, endpoint ou chave institucional (apenas o nome público "Devel" e referência ao fórum).
- [x] 1. `chore: estrutura inicial, .gitignore e dependências declaradas` — `git ls-files` cobre `.gitignore`/`requirements.txt`; `.env` ausente do índice. O `.gitignore` já cobre `.env`, venv e caches desde aqui (decisão 0.7), não apenas no Intermediário.
  **Commit `ed88088`** (2026-11-08): `requirements.txt` (`openai` + `python-dotenv` + `pytest`) e
  `.python-version` (`3.12`). Verificado: `git ls-files` cobre `.gitignore`/`requirements.txt`, `.env`
  fora do índice, varredura de segredo limpa.
- [x] 2. `test(basico): casos de entrada vazia e configuração ausente` (vermelhos) — `pytest` falha exatamente nesses dois casos.
  **Layout adotado:** `src/` (`entrada.py`, `config.py`) + `tests/` + `pytest.ini` (`pythonpath=.`).
  Stubs lançam `AssertionError` (não `NotImplementedError`, que é subclasse de `RuntimeError` e faria
  os testes passarem por acidente). Evidência: `.venv/bin/python -m pytest -q` → **4 failed** (entrada
  vazia, só-espacos, credencial ausente, não-expor-segredo), todos vermelhos pelo motivo correto.
- [x] 3. `feat(basico): leitura e validação da entrada textual` (+ testes verdes) — `test_entrada.py` verde.
  **Implementação:** `src/entrada.py::validar_entrada()` normaliza bordas/quebras, bloqueia vazia com
  orientação (contém "ingredientes") e barra texto > `MAX_ENTRADA_CHARS` (5000) antes da API. Evidência:
  `.venv/bin/python -m pytest tests/test_entrada.py -q` → **4 passed** (vazia, só-espacos, feliz, longo).
- [x] 4. `feat(basico): preparo e envio da solicitação ao LLM com config externa` — chamada real responde (evidência "Entrada válida").
  **Implementação:** `src/config.py::carregar_config()` lê `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` do
  ambiente e levanta `ConfiguracaoAusenteError` citando só o NOME faltante (nunca o valor). Parâmetro
  `carregar_arquivo=False` permite testes sem o `.env` real sobrescrever o cenário simulado.
  `src/llm.py::analisar_ingredientes()` monta system+user e chama a API compatível com OpenAI; ponto de
  entrada `src/app.py` orquestra os 4 passos. Evidência: suíte → **6 passed**; `python -m src.app` com
  amostra fictícia retornou painel de alertas (glúten/soja/Tartrazina, lactose ausente) + tabela de
  aditivos com INS — chamada real ao modelo institucional funcionando. **Commit `79b8040`**
  (2026-11-08): inclui também a decisão 0.8 (UX da entrada multi-linha).
- [x] 5. `feat(basico): processamento e apresentação da resposta` — fluxo de 4 passos completo no terminal.
  **Implementação:** `src/llm.py::processar_resposta()` (passo 3) normaliza a forma do texto — trim nas
  bordas e colapso de 3+ quebras em no máximo 2, preservando parágrafos; não reinterpreta conteúdo.
  `src/app.py::apresentar()` (passo 4) isola a formatação da saída (cabeçalho + corpo + aviso fixo de
  caráter informacional) e sinaliza texto vazio sem imprimir nada. `main()` passa a orquestrar os 4
  passos nomeados. Evidência: suíte → **6 passed**; smoke de `processar_resposta` confirma colapso de
  quebras; `python -m src.app` via pipe com amostra fictícia retornou painel de alertas + tabela de
  aditivos formatados e o aviso informacional — ciclo de 4 passos completo com chamada real.
- ~~6. `test(basico): tratamento de resposta ausente com integração simulada`~~ — **removido do Básico
  pela decisão 0.10**: o mock pertence ao Avançado (item 3 daquela sequência), onde o enunciado o pede.
- [x] 7. `docs(basico): README com instalação, execução e justificativa do LLM` — README permite executar seguindo só o texto.
  **Implementação:** `README.md` reescrito a partir do placeholder — problema, público, justificativa
  do LLM, limites de escopo, instalação (venv + pip, comando genérico único `python -m venv .venv`),
  configuração via `.env.example`, execução (terminal interativo e por pipe), exemplo de saída alinhado
  ao formato real, testes, estrutura e limitações. Versão Python documentada como **3.12+** (base 3.12.3;
  validado também em 3.13 e 3.14.7). Evidência: scan de segredo no staged diff **LIMPO**; comando
  documentado `python -m pytest` produz exatamente as **6 passed** prometidas; exemplo de pipe executado
  com exit 0. **Commit `4073d29`** (2026-11-08): inclui também a correção de coerência dos comentários de
  `src/llm.py` que apontavam para o antigo item 6 (agora Intermediário/Avançado, decisão 0.10).
- [x] 8. `feat(basico): .env.example e cobertura do .gitignore` *(antecipado pelo decisão 0.7)* —
  `.env.example` presente com **apenas nomes de variáveis** (sem valor real, sem endpoint,
  sem modelo institucional); `git check-ignore -v .env` confirma que `.env` é ignorado; varredura
  do staged diff não encontra cadeia de segredo.
  **Implementação:** `.env.example` criado com os três nomes (`LLM_BASE_URL` / `LLM_API_KEY` /
  `LLM_MODEL`) e valores-placeholder genéricos; cabeçalho orienta `cp .env.example .env` e adverte que o
  repositório é público. Evidência: `git check-ignore .env` confirma o ignore; varredura do staged diff
  **LIMPO** (nenhum endpoint/nome comercial/`sk-`). **Commit `52f5d17`** (2026-11-08): registra também a
  decisão 0.11 (substituição por provedor externo durante desenvolvimento, sem publicar dados restritos).

### Pendências de UX registradas (fora do escopo dos itens acima)

Nada aqui é implementação autorizada ainda — entram no plano para execução futura mediante
aprovação, cada uma em seu próprio commit. Registradas porque foram levantadas durante o
desenvolvimento mas **não** constavam do plano quando tentadas (regra: nenhuma implementação
fora do plano).

- [ ] **UX-1 · indicador de processamento durante a chamada ao LLM.** A chamada é síncrona e
      pode levar de segundos a mais de um minuto (modelo com raciocínio); hoje a tela fica só
      com o cursor piscando. Opções avaliadas: **(A)** imprimir `"Analisando… (aguarde)"` antes
      de bloquear (banal, 1 linha em `src/app.py`, sem tocar testes); **(B)** spinner animado
      (`threading`); **(C)** streaming real (`stream=True`), que altera `analisar_ingredientes()`
      e a validação de resposta vazia → pertence ao **nível Avançado**, junto com parâmetros
      configuráveis. Decisão: aplicar **(A)** em commit próprio quando aprovado; **(C)** fica
      reservado para o Avançado. *(Levantado no item 4; NÃO implementado — removido por decisão
      do aluno por estar fora do plano.)*

Cada item segue o ciclo **uma fatia → testes → diff → aprovação → commit**; nenhum item novo
começa enquanto houver mudanças pendentes de aprovação, e nenhum nível novo inicia sem ordem
explícita do usuário. **Push é sempre executado manualmente pelo aluno** (os tags `p0-*` também
só vão ao remoto por ação do usuário).

**Gate de saída:** checklist Básico do `AGENTS.md` completo **+ item 8 acima** + chamada real
funcionando ("Entrada válida") → tag `p0-basico` (com aprovação separada).
Atualizar linha **NÍVEL ATUAL** → `INTERMEDIÁRIO`.

---

## Nível 2 — INTERMEDIÁRIO (organização e tratamento de erros)

**Objetivo:** amadurecer a **mesma** aplicação — refinar as fronteiras entre módulos e
fechar a **matriz completa de erros** exigida pelo checklist do `AGENTS.md`.

> A separação de responsabilidades já foi construída no Básico (`src/entrada.py`,
> `config.py`, `llm.py`, `app.py`). Aqui ela é **refinada à luz dos erros**, não refeita do zero
> (evita refactor fake). Ver item 3.

### Matriz de erros (mapeada 1:1 ao checklist Intermediário)

Todo cenário abaixo é **tratado** no Intermediário (item 4) com mensagem compreensível, sem
stack trace crua nem segredo exposto. Os testes nomeados exercitam o tratamento; quando o
enunciado só admite via integração simulada, o **teste offline** fica no Avançado (decisão 0.12).

| # | Cenário (checklist) | Como é demonstrado no Intermediário | Evidência |
| --- | --- | --- | --- |
| 1 | Configuração ausente ou inválida | `test_config.py` (estende o do Básico): variável faltando ou malformed → erro claro citando só o nome | "config ausente/inválida" |
| 2 | Credencial ausente | `test_config.py`: `LLM_API_KEY` vazio → encerramento controlado, sem vazar valor | "credencial ausente" |
| 3 | Credencial inválida | `test_rede.py` com cliente simulado: API devolve 401 → mensagem de autenticação, sem ecoar chave | "credencial inválida" |
| 4 | Indisponibilidade do LLM | `test_rede.py`: API devolve 5xx / conexão recusada → orienta tentar mais tarde | "indisponibilidade" |
| 5 | Falha de comunicação / timeout | `test_rede.py`: exceção de rede / estouro de prazo → distingue timeout de queda | "falha de comunicação · timeout" |
| 6 | Resposta vazia ou formato inesperado | `test_resposta.py` (chamada real pode vir vazia): corpo ausente/inesperado → tratamento legível; **teste offline** no Avançado (0.12) | "resposta vazia/formato inesperado" |

### Sequência de commits prevista (branch + PR obrigatórios)

- [x] 1. branch `intermediario/tratamento-erros` criada a partir do estado entregue do Básico
  (HEAD `8a597da`, mesmo commit da tag `p0-basico`). **Evidência:** primeiro commit aprovado na
  branch — `33d0618` (`docs(plano): amplitude dos testes vermelhos do item 2 — decisão 0.13`).
- [x] 2. `test(intermediario): bateria vermelha da matriz de erros (6 cenários)` — `pytest` falha nos casos ainda não tratados, distribuídos por arquivo (decisão 0.13): `test_rede.py` novo (credencial inválida → 401, indisponibilidade → 5xx/conexão recusada, timeout) usando cliente simulado que lança as exceções reais da lib `openai`; extensão de `test_config.py` (config malformed / variável inválida); `test_resposta.py` só para o tratamento de corpo vazio/formato inesperado numa chamada real. Vermelhos pelo motivo correto: importam a camada de tratamento (`src/erros.py`) que ainda não existe. O **mock offline completo** fica reservado ao Avançado (decisão 0.12).
  **Evidência:** commit `f7d2e7c` — 3 collection errors por `ImportError: cannot import name 'erros' from 'src'` (vermelho pelo motivo certo); `test_entrada.py` segue com 4 passed (sem regressão).
- [x] 3. `refactor(intermediario): refinar fronteiras entre módulos à luz da matriz de erros` — extração do tratamento de exceções para camada própria (ex.: separar mapeamento de erro de rede/resposta dentro de `llm.py`), sem reorganizar o que o Básico já modularizou. Testes do Básico continuam verdes (sem regressão).
  **Evidência:** commit `e77fa24` — `src/erros.py` com `ErroDeLlm` + 5 subclasses e as assinaturas `chamar_llm`/`validar_resposta`/`validar_configuracao` (corpos em `NotImplementedError`, preenchidos no item 4). Nenhum módulo do Básico alterado; suíte passa de `ImportError` a `NotImplementedError` → 6 verdes / 6 vermelhos.
- [x] 4. `feat(intermediario): tratamento controlado da matriz de erros` (+ testes verdes) — cobre os **seis** cenários da matriz acima; `test_rede.py` e extensões de `test_config.py`/`test_resposta.py` verdes; nenhuma mensagem crua de exceção; nenhum segredo exposto.
  **Evidência:** commit `982ac3e` — `chamar_llm` traduz as exceções do cliente OpenAI em `ErroDeAutenticacao`/`ErroTimeout`/`ErroIndisponibilidade`/status≥500; `validar_resposta` rejeita vazia/formato inesperado; `validar_configuracao` confere a URL sem expor a chave; `app.py` roteia cada família para mensagem curta no stderr com exit code existente (decisão 0.14). Suíte: **12 passed**. Smoke: base URL malformada → `[configuração]` exit 2; porta morta → `[LLM]` exit 1.
- [x] 5. `test(intermediario): consistência entre`.env.example` e as variáveis lidas por `config.py`` — artefatos criados no Básico (decisão 0.7); aqui apenas se confere que todo nome declarado no template é de fato consumido pelo código, e que nenhum valor real aparece.
  **Evidência:** cotejo por comando — nomes declarados em `.env.example` (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`) são idênticos aos lidos em `src/config.py::VARIAVEIS_OBRIGATORIAS`; nenhum sobra nem falta dos dois lados. Scan do template contra padrões de segredo → LIMPO (só placeholders: `substitua-pelo-endpoint-do-servico`, `cole-aqui-sua-chave-sem-publicar`, `substitua-pelo-nome-do-modelo`). Sem código novo; verificação concluída sem commit próprio (registrada aqui).
- [x] 6. `docs(intermediario): exemplos de entrada/saída e distinção testes reais × simulados` — README atualizado.
  **Evidência:** README ganhou a seção *Testes simulados × chamada real* (os 12 testes rodam offline com cliente falso; a chamada real é demonstrada só via `python -m src.app`, sem credencial em teste), a tabela *Tratamento de erros* com as mensagens literais do código e seus exit codes, contagem corrigida para `12 passed`, cobertura dos quatro arquivos de teste, estrutura com `erros.py` + novos testes, e limitação antiga ("timeout propaga exceção técnica") substituída pelo estado real do Intermediário. Exemplo de entrada/saída já presente desde o Básico foi mantido.
- [ ] 7. PR → merge para `master` (branch real do repositório) — PR linkado no histórico.

**Gate de saída:** checklist Intermediário do `AGENTS.md` completo → tag
`p0-intermediario`. Atualizar **NÍVEL ATUAL** → `AVANÇADO`.

---

## Nível 3 — AVANÇADO (entrega reproduzível)

**Objetivo:** alguém fora do projeto clona, configura e executa sem ajuda.

### Testes/evidências primeiro

| Artefato | Cenário coberto | Evidência mínima |
| --- | --- | --- |
| suíte local offline | ≥1 teste de lógica sem chamada real ao LLM | "Teste sem chamada real" |
| varredura do histórico (`git log -p`) | nenhuma credencial em código ou histórico | "Proteção de segredo" |
| validação em venv limpa seguindo só o README | instalação/execução por terceiro | "Ambiente limpo" |

### Sequência de commits prevista

- [ ] 1. `feat(avancado): parâmetros do LLM ajustáveis por configuração externa` — mudar token/temperatura no `.env` altera a requisição sem editar código.
- [ ] 2. `feat(avancado): registros de execução sem segredos nem dados pessoais` — log inspecionado não contém chave nem conteúdo sensível.
- [ ] 3. `test(avancado): suíte local executável sem chamada real ao LLM` — `pytest` completo passa offline. Inclui o `test_resposta.py` de **resposta ausente/vazia com integração simulada**, movido do Básico pela decisão 0.10.
- [ ] 4. `chore(avancado): validação em ambiente limpo e correções registradas` — venv nova segue só o README; problemas/correções anotados no relatório.
- [ ] 5. `docs(relatorio): decisões, evolução entre níveis, falhas, uso de IA e limitações` — relatório cobre os seis tópicos do vídeo.
- [ ] 6. `docs(readme): versão do Python, bibliotecas e acesso aos artefatos` — README final revisado (sem duplicar relatório).

**Gate de saída:** checklist Avançado do `AGENTS.md` completo + relatório + vídeo
≤5 min (não listado, legendas revisadas, sem credenciais na tela) → tag
`p0-avancado` ← **estado avaliado pela banca**.

---

## Pós-código (no Moodle, fora do repositório)

- Submissão única: link do repositório + tag `p0-avancado`, até 06/12/2026.
- Avaliação por pares: 2 entregas completas de autores distintos no Laboratório de
  Avaliação — justificar com evidências dos artefatos (o formulário pergunta se os
  testes cobrem sucesso **e** falha; o plano acima garante essa resposta).

---

## Riscos e mitigação

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Problema amplo demais | entrega "menos avançada" na banca | regra de escopo do AGENTS.md; problema em uma frase |
| Derivar para conselho médico/nutricional | risco ético + fora do escopo P0 | fronteira explícita na Fase 0; prompt restringe a decodificação informacional |
| Falso negativo em alérgeno (alerta ausente) | pior falha possível — consumidor exposto | teste de robustez com derivados ocultos (*caseinato*, *malte*); saída sempre cita o termo original, permitindo auditoria manual pelo usuário |
| Segredo ou endpoint institucional publicado | repo público → vazamento irreversível | revogar credencial + scan antes de cada commit (trava do AGENTS.md); `.env` fora do índice |
| Um único commit final | histórico sem evolução (critério "Processo e autoria") | sequência acima; commits pequenos aprovados em review |
| Escorregar do prazo 06/12 | entrega perdida | tags por nível como checkpoints; hoje: 08/11 |

## Protocolo de marcação (como fechar um item)

Estado do projeto = este arquivo. Regras:

1. **Critério objetivo:** item vira `- [x]` somente quando (a) o commit correspondente
   foi **aprovado pelo usuário e executado**, e (b) a evidência verificável citada na
   linha existe (teste verde, arquivo presente, checklist do `AGENTS.md` satisfeito).
   "Quase pronto" fica `- [ ]`.
2. **Quem marca:** o agente marca após confirmar (a)+(b), apresentando a linha alterada
   no diff seguinte; o usuário também pode marcar/editar manualmente quando quiser.
3. **Como o agente verifica ao iniciar uma sessão:** ler `PLANO.md` → conferir o
   **NÍVEL ATUAL** no `AGENTS.md` → localizar o primeiro `- [ ]` da sequência desse
   nível → validar pré-requisitos (itens anteriores `[x]`, Fase 0 respondida, gate do
   nível anterior fechado com tag existente via `git tag`). Se algum `[x]` não bater com
   a evidência, **sinalizar a divergência** em vez de assumir o estado.
4. **Auditoria:** como o plano é commitado, o histórico do Git mostra *quando* cada item
   fechou — evidência de evolução para o critério "Processo e autoria".
5. Gate de nível continua sendo o checklist do `AGENTS.md` + tag (aprovação separada);
   checkbox de item individual **não** substitui gate.

## Revisão do plano

Este plano é estático e mantido à mão: revisar ao fechar cada nível (marcar itens
concluídos, registrar desvios e problemas encontrados na validação em ambiente
limpo). Não automatizar execução nem delegar commits ao agente — trava de
permissão explícita por conversa permanece absoluta.
