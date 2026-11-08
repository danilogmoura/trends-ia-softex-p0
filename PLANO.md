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
| `test_resposta.py` | resposta ausente/vazia tratada (mock, sem rede) | "Teste sem chamada real" |

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
  app.py       # orquestra o ciclo de 4 passos (itens 4–5)
  entrada.py   # validar_entrada()      — item 3
  config.py    # carregar_config()      — item 4
  llm.py       # preparar/enviar + processar resposta — itens 4–5
tests/         # test_entrada, test_config, test_resposta
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
- [ ] 4. `feat(basico): preparo e envio da solicitação ao LLM com config externa` — chamada real responde (evidência "Entrada válida").
- [ ] 5. `feat(basico): processamento e apresentação da resposta` — fluxo de 4 passos completo no terminal.
- [ ] 6. `test(basico): tratamento de resposta ausente com integração simulada` — `test_resposta.py` verde offline.
- [ ] 7. `docs(basico): README com instalação, execução e justificativa do LLM` — README permite executar seguindo só o texto.
- [ ] 8. `feat(basico): .env.example e cobertura do .gitignore` *(antecipado pelo decisão 0.7)* —
  `.env.example` presente com **apenas nomes de variáveis** (sem valor real, sem endpoint,
  sem modelo institucional); `git check-ignore -v .env` confirma que `.env` é ignorado; varredura
  do staged diff não encontra cadeia de segredo.

Cada item segue o ciclo **uma fatia → testes → diff → aprovação → commit**; nenhum item novo
começa enquanto houver mudanças pendentes de aprovação, e nenhum nível novo inicia sem ordem
explícita do usuário. **Push é sempre executado manualmente pelo aluno** (os tags `p0-*` também
só vão ao remoto por ação do usuário).

**Gate de saída:** checklist Básico do `AGENTS.md` completo **+ item 8 acima** + chamada real
funcionando ("Entrada válida") → tag `p0-basico` (com aprovação separada).
Atualizar linha **NÍVEL ATUAL** → `INTERMEDIÁRIO`.

---

## Nível 2 — INTERMEDIÁRIO (organização e tratamento de erros)

**Objetivo:** amadurecer a **mesma** aplicação — separar responsabilidades e fechar
a matriz de erros.

### Testes primeiro

| Teste | Cenário coberto | Evidência mínima |
| --- | --- | --- |
| `test_config.py` (extensão) | credencial inválida → encerramento controlado | "Credencial inválida" |
| `test_rede.py` | falha de comunicação e timeout → mensagem compreensível | "Falha de comunicação" |
| `test_resposta.py` (extensão) | resposta em formato inesperado | matriz de erros |

### Sequência de commits prevista (branch + PR obrigatórios)

- [ ] 1. branch `intermediario/tratamento-erros` criada a partir de `p0-basico`.
- [ ] 2. `test(intermediario): credencial inválida, indisponibilidade e timeout` (vermelhos) — `pytest` falha nesses casos.
- [ ] 3. `refactor(intermediario): separar entrada, config, solicitação, chamada, resposta e saída` — testes do Básico continuam verdes (sem regressão).
- [ ] 4. `feat(intermediario): tratamento controlado da matriz de erros` (+ testes verdes) — `test_rede.py` e extensões verdes; nenhuma mensagem crua de exceção.
- [ ] 5. `test(intermediario): consistência entre`.env.example` e as variáveis lidas por `config.py`` — artefatos criados no Básico (decisão 0.7); aqui apenas se confere que todo nome declarado no template é de fato consumido pelo código, e que nenhum valor real aparece.
- [ ] 6. `docs(intermediario): exemplos de entrada/saída e distinção testes reais × simulados` — README atualizado.
- [ ] 7. PR → merge para `main` — PR linkado no histórico.

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
- [ ] 3. `test(avancado): suíte local executável sem chamada real ao LLM` — `pytest` completo passa offline.
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
