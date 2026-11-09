# Agente padrão do projeto — Primeiro fluxo com LLM

Estas instruções se aplicam automaticamente a **todo** trabalho neste repositório.
Cobrem os três níveis (Básico, Intermediário, Avançado) num único arquivo que evolui junto com o projeto.

## >>> NÍVEL ATUAL: INTERMEDIÁRIO <<<

Edite **apenas esta linha** conforme o projeto evoluir: `BÁSICO` → `INTERMEDIÁRIO` → `AVANÇADO`.
Trabalhe **somente** na seção correspondente ao nível atual. Não antecipe exigências de níveis
futuros nem retroceda decisões já consolidadas.

**Trava de nível (regra absoluta):** avançar para o próximo nível (especialmente Intermediário e
Avançado) **somente quando o usuário ordenar explicitamente**, com o nível anterior já entregue
(testes verdes + commit aprovado). Nunca iniciar código, refatoração ou planejamento-execução do
nível seguinte por iniciativa própria — mesmo que a oportunidade pareça natural.

## Janela de entrega (calendário oficial)

O percurso deste aluno começa no **Bloco 0 (nivelamento)**. Datas do calendário oficial
(Guia do Aluno TrendsIA — "Calendário e prazos"):

| Projeto | Início | Entrega |
| --- | --- | --- |
| **P0** | 03/11/2026 | **06/12/2026** |

Planeje os três níveis (Básico → Intermediário → Avançado) dentro da janela do P0; a entrega
oficial é uma única submissão no Moodle até **06/12/2026**. Fontes completas por bloco:
`../softex-sistemas-agentes/docs/moodle/calendario-e-prazos.md`.

## Fonte de verdade

Regras vêm do enunciado oficial. Antes de afirmar qualquer exigência, confira em:

- `../softex-sistemas-agentes/docs/moodle/p0/p0-primeiro-fluxo-com-llm.md`
- `../softex-sistemas-agentes/docs/moodle/orientacoes-gerais/orientacoes-gerais-e-convencoes.md`
  (quadro C01–C29, hierarquia das regras, segurança/LGPD)
- `../softex-sistemas-agentes/docs/moodle/calendario-e-prazos.md` (datas de entrega por bloco)

**NUNCA invente requisito.** Se algo não estiver no enunciado, diga `_([não presente no enunciado]_)`
e registre como decisão pendente do aluno.

## Plano de execução

A sequência de trabalho, os testes por nível e os gates de cada tag estão em `PLANO.md`
(este repositório). Antes de propor código: verificar o **NÍVEL ATUAL**, localizar o próximo
item pendente do plano e confirmar se a Fase 0 (decisões do aluno) já está respondida — sem
problema escolhido, nenhum `feat` tem especificação válida. O plano guia mas não é lei rígida:
desvios registrados no próprio `PLANO.md` alimentam o relatório de decisões.

## Regras transversais (valem nos três níveis)

### Escopo proibido no P0 inteiro

Não construir: aplicação web, interface gráfica, app móvel, autenticação de usuários, banco de
dados, RAG, agentes autônomos, múltiplos agentes, comparação entre modelos, implantação em nuvem,
treinamento/ajuste de modelos.

Faz parte: Python, execução local, **um único LLM**, entrada/saída textuais, Git/GitHub, tratamento
básico de erros, testes, documentação.

> Escolher problema excessivamente amplo **não** torna a entrega mais avançada. No P0, maturidade =
> resolver bem um problema pequeno.

Princípio geral do curso: *"a complexidade deve ser consequência do problema, não um objetivo
isolado"* — escolher a alternativa mais simples capaz de resolver com qualidade. Arquitetura
sofisticada sem justificativa aumenta risco, dificulta testes e atrapalha manutenção.

### Uso de IA no desenvolvimento (C14)

IA pode apoiar código, testes, documentação e análise, mas **autoria, compreensão e responsabilidade
continuam sendo do aluno**. Todo código gerado/alterado por IA deve ser **revisado e testado** antes
de ser incorporado. Registrar no relatório apenas as interações que influenciaram significativamente:
ferramenta/modelo · tarefa delegada · resultado aproveitado · correções/descartes · forma de
verificação. Não reproduzir conversas completas nem cadeias de raciocínio interno do modelo.

### Segurança e dados (absoluta)

- Chaves, tokens e parâmetros sensíveis **nunca** no código nem enviados ao GitHub.
- Credenciais não podem aparecer em **código, repositório, logs, relatórios, vídeos ou interfaces**.
- Adicionar ao `.gitignore` **depois** que o segredo foi publicado **não apaga** o histórico → revogar a credencial.
- **Dados (LGPD / C08)**: usar apenas dados fictícios, públicos, próprios, autorizados ou devidamente
  anonimizados. Não coletar nem armazenar dados pessoais sem necessidade.
- Decisões de alto impacto (saúde, crédito, seleção, sanções, segurança, direitos): a IA fica em papel
  **informacional, preliminar ou supervisionado**; a decisão final permanece humana.

### LLM institucional

A instituição definiu um provedor/modelo institucional, apresentado pela equipe de suporte no
fórum do P0 (tópico "[LLM] Devel"). **Detalhes de servidor (URL, hostname, endereço, modelo exato)
não vão neste arquivo** — o P0 será entregue em repositório **público**. Consulte sempre a fonte
interna:

- Base de conhecimento local: `../softex-sistemas-agentes/docs/moodle/kb/forum-qa.md` (tópico
  "[LLM] Devel") e `../softex-sistemas-agentes/docs/moodle/extracao-manual/manual-do-aluno-devel.md`.
- Suporte: **ticket na plataforma Devel**; acesso mediante cadastro + aprovação + agendamento.

Regras operacionais (do manual): usar **sempre o hostname fornecido**, nunca substituir por IP; o
firewall libera somente o destino/porta indicados; erro TLS → conferir certificados CA, data/hora e
a URL exatamente como fornecida; indisponibilidade durante a reserva → seguir a orientação do
fórum/manual.

No código do P0: **nada hardcoded**. Base URL, chave e modelo vêm de configuração externa (`.env`,
fora do versionamento). Registre no relatório qual provedor/modelo foi usado — sem publicar
credenciais nem dados restritos. Se substituir o institucional, os custos são do aluno e a
instituição não dá suporte ao serviço.

### Git e repositório

- **Trava de commit (regra absoluta do aluno):** nenhum `git commit`, `git tag` ou `git push` é executado
  sem **permissão explícita na conversa atual**. O fluxo é: o agente edita → roda testes → **apresenta o
  diff para code review do usuário** → aguarda aprovação → só então commite. "Prossiga"/"ok" genérico não
  conta como aprovação de commit; precisa de pedido direto. Se a regra for violada, desfazer com
  `git reset --soft HEAD~1` e avisar o usuário.
- **Trava de push (regra absoluta):** `git push` — e qualquer operação de envio a remoto (`push --tags`,
  force-push, publicação de release) — é **sempre executado manualmente pelo usuário**, nunca pelo
  agente, mesmo mediante pedido na conversa. O papel do agente termina no commit local aprovado; se
  houver necessidade de publicar, o agente informa os commits prontos e aguarda o push do usuário.
- **Ao receber o pedido de commit**, o agente executa nesta ordem:
  1. `git status` + `git diff` — analisar todas as mudanças reais (não presumir do que lembra da sessão);
  2. conferir que nenhum segredo, endpoint ou modelo institucional está no staged diff (repo público);
  3. **gerar a mensagem Conventional Commits em PT-BR derivada do conteúdo do diff** — tipo conforme a
     natureza da mudança (`feat` nova implementação · `fix` correção · `docs` documentação · `test`
     testes · `refactor` reorganização sem mudança de comportamento · `chore` infraestrutura), escopo
     opcional identificando a parte afetada;
  4. apresentar mensagem + resumo ao usuário e executar o commit; `push` e `tag` exigem aprovação separada.
- Commits **pequenos e coerentes**; o histórico deve mostrar **evolução real** — nunca um commit único
  final pouco antes da entrega.
- **Nunca continuar a implementação antes do commit (regra absoluta):** cada fatia de trabalho termina
  em commit aprovado. Enquanto houver mudanças pendentes de aprovação, nenhuma funcionalidade nova é
  iniciada — primeiro fecha-se o commit da fatia atual, só depois se começa a próxima.
- PT-BR, Conventional Commits: `feat:` nova implementação · `fix:` correção · `docs:` documentação. Escopo opcional: `feat(p0): ...`.
- Repositório **público** (obrigatório para a avaliação por pares). Materiais restritos ficam fora do
  repo público; na entrega usar amostras fictícias — vale também para histórico, tags e artefatos.
- **Registro inicial**: criar o repositório público no início do projeto e informar o endereço na
  atividade "Registro inicial do repositório" no Moodle (sem nota própria). Manter o mesmo
  repositório durante todo o desenvolvimento.
- Branch + pull request: exigido no P0 a partir do nível Intermediário.

### Decisões que cabem ao aluno (pergunte, não presuma)

- [ ] qual **problema** será resolvido (explicável em uma frase)
- [ ] **quem** possui essa necessidade
- [ ] qual será a **entrada** / qual será a **saída**
- [ ] **por que um LLM é adequado** (se regra fixa resolve mais simples, talvez não seja a escolha)
- [ ] como será usada a **interface de acesso** ao LLM escolhido

### Hierarquia das regras (ordem de interpretação)

1. Enunciado específico do projeto (P0) — prevalece quando for mais detalhado ou restritivo.
2. Orientações gerais.
3. Comunicados oficiais da coordenação.
4. Decisões registradas no acompanhamento ou na mentoria.

Exigência que aparece só em outro projeto **não** se transfere automaticamente ao P0.
Antes de iniciar, confirmar cinco pontos: qual é o problema · qual é o resultado esperado · quais
decisões cabem ao aluno · quais são os limites do escopo · quais evidências precisam ser entregues.

## Competências do P0 (C01–C04)

| Cód. | Competência |
| --- | --- |
| C01 | Desenvolvimento de código Python para aplicações de IA |
| C02 | Versionamento com Git e GitHub |
| C03 | Integração com serviços externos por APIs REST |
| C04 | Ambiente de desenvolvimento funcional e reproduzível |

Transversais avaliadas em todas as entregas: **C14** (desenvolvimento assistido por IDEs agênticas —
delegar revisando, testando e compreendendo) e **C08** (riscos éticos e conformidade com a LGPD).

---

## Nível Básico — primeiro fluxo funcional

Construir exatamente as quatro partes do ciclo central:

1. receber uma **entrada textual** (terminal é suficiente);
2. **preparar e enviar** a solicitação ao modelo;
3. **processar** a resposta recebida;
4. **apresentar** o resultado ao usuário.

Já obrigatório nesta etapa: dependências **declaradas** e credencial/configuração sensível **fora do código**.

Testes: sempre que o problema permitir, não testar apenas o cenário ideal — incluir entrada
incompleta, ambiguidade, solicitação fora do escopo, falha técnica, resposta ausente e necessidade de
intervenção humana. Resultado desfavorável não se esconde: uma falha bem investigada é evidência de
aprendizagem tão importante quanto um teste bem-sucedido.

**Checklist de conclusão:**

- [ ] Problema descrito em uma frase (quem / o que entra / o que sai)
- [ ] Justificativa de por que usar LLM registrada
- [ ] Fluxo de 4 passos funcionando com entrada do terminal
- [ ] Chamada real a **um** LLM funcionando
- [ ] Dependências declaradas (`requirements.txt`) + versão do Python
- [ ] Nenhuma credencial no código (`git log -p` limpo)
- [ ] Provedor/modelo escolhidos documentados
- [ ] Commits pequenos e coerentes
- [ ] Tag `p0-basico` criada

Ao fechar: atualize a linha **NÍVEL ATUAL** para `INTERMEDIÁRIO`.

---

## Nível Intermediário — organização e tratamento de erros

Evoluir a **mesma** aplicação (não começar outro projeto).

Separar responsabilidades que hoje estão misturadas num único bloco:
captura da entrada · carregamento da configuração · preparação da solicitação · chamada ao modelo ·
tratamento da resposta · apresentação do resultado.

Impedir entradas vazias e tratar de forma controlada, com mensagens compreensíveis (não encerrar com
erro técnico extenso sem explicar):

- configuração de acesso ausente ou inválida
- credencial ausente
- credencial inválida
- indisponibilidade do LLM escolhido
- falha de comunicação
- timeout
- resposta vazia ou em formato inesperado

Demonstrar **credencial ausente** e **credencial inválida** sem expor segredos. Se o serviço escolhido
não exigir autenticação, esses cenários podem ser demonstrados por testes com integração simulada,
mantendo a chamada real ao LLM para provar o funcionamento.

Incluir também: `.env.example` sem credenciais reais · `.gitignore` adequado · instruções de
instalação/configuração/execução · exemplos de entrada e saída · pelo menos **uma branch** integrada
à principal por **pull request**.

Competências: C01 funções com responsabilidades claras · C02 branch/commits/PR registrando evolução ·
C03 tratar erros de autenticação/comunicação/resposta · C04 documentar instalação e configuração p/ terceiros.

**Checklist de conclusão:**

- [ ] Responsabilidades separadas em funções/módulos distintos
- [ ] Entrada vazia bloqueada com orientação ao usuário
- [ ] Cada cenário de erro acima tratado com mensagem compreensível
- [ ] Credencial ausente e inválida demonstradas (real ou simulada), sem vazar segredo
- [ ] `.env.example` presente e sem valor real
- [ ] `.gitignore` cobre `.env`, venv, caches
- [ ] README com instalação, configuração, execução e exemplos de entrada/saída
- [ ] Documentação distingue testes reais dos simulados
- [ ] Branch de desenvolvimento fundida à principal via PR
- [ ] Tag `p0-intermediario` criada

Ao fechar: atualize a linha **NÍVEL ATUAL** para `AVANÇADO`.

---

## Nível Avançado — entrega reproduzível

Transformar a solução em entrega pequena, mas tecnicamente completa.

- Configurações da interface do LLM (limite de tokens, parâmetros de geração, comportamento básico)
  devem poder mudar **sem modificar o núcleo** do programa.
- Registros simples de execução, **sem** armazenar chaves, tokens, credenciais, dados pessoais ou
  conteúdo sensível desnecessário.
- Documentar versão do Python e principais bibliotecas.
- Pelo menos **um teste de lógica local** executável sem chamada real ao LLM (validação da entrada,
  preparação da solicitação, carregamento da configuração, tratamento de resposta simulada, ou de
  erro simulado).
- Validar em **ambiente limpo**: novo venv, outra máquina, ou outra pessoa seguindo apenas o README.
  Se a validação revelar problema, registrar o que aconteceu e a correção.

Competências: C01 código compreensível para terceiros · C02 histórico do Git como evidência real ·
C03 lidar com respostas/falhas sem expor informação sensível · C04 instalar e executar em ambiente
diferente do de desenvolvimento.

Resultado esperado: alguém fora do projeto consegue clonar, preparar o ambiente, configurar o acesso
e executar sem sua ajuda.

**Checklist de conclusão:**

- [ ] Parâmetros do LLM ajustáveis por configuração externa (sem editar o núcleo)
- [ ] Logs presentes e comprovadamente livres de segredo/dado pessoal
- [ ] Versão do Python e bibliotecas documentadas
- [ ] ≥1 teste local sem chamada real ao LLM passando
- [ ] Validação em ambiente limpo realizada e registrada (com problemas e correções, se houve)
- [ ] Histórico do Git mostra a evolução entre os três níveis
- [ ] Tag `p0-avancado` criada ← **estado avaliado pela banca**

---

## Entrega oficial, documentação e pós-código

### Como o Moodle registra a entrega

- GitHub armazena os artefatos; **o Moodle registra oficialmente a entrega**.
- **Uma única entrega final** por projeto: na atividade indicada, submeter o **link do repositório +
  a tag/release do nível Avançado** (identifica a versão entregue). As tags Básico e Intermediário
  permanecem disponíveis no repositório para consulta na avaliação final.
- Data de entrega = data da submissão no Moodle. O conteúdo avaliado é o estado do repositório
  **identificado pela tag informada**; alterações posteriores não substituem a versão entregue.
- O repositório deve conter **todos** os artefatos avaliados: código-fonte · `README.md` · arquivo de
  dependências · `.env.example` sem segredos · `.gitignore` adequado · casos de teste ·
  **relatório de execução** · **link do vídeo** · tags/releases dos três níveis.

### Divisão README × relatório (não duplicar)

- **README**: somente informações necessárias à instalação, configuração, execução, testes, estrutura
  do repositório, limitações e acesso aos demais artefatos.
- **Relatório**: registrar decisões e evidências — evolução entre níveis, testes, falhas, limitações,
  uso de IA, reflexão final. Não repetir integralmente o README nem virar diário de todas as ações.
- Ambiente executável exige documentar: versão da linguagem · dependências · variáveis de ambiente ·
  comandos/etapas de instalação · forma de execução · forma de testar · limitações conhecidas.

### Vídeo obrigatório (P0: máximo 5 minutos)

- Publicado no YouTube como **não listado**; link informado na entrega.
- Gravação de tela com narração é suficiente; mostrar o rosto não é necessário; slides podem apoiar
  mas **não substituem** a demonstração — execução e registros reais ocupam parte relevante.
- **Legendas automáticas revisadas** (ou transcrição equivalente) são obrigatórias; a narração descreve
  as ações, resultados e elementos da tela; código, tabelas e terminal legíveis; áudio compreensível.
- **Credenciais e dados sensíveis não podem aparecer.**
- Seis tópicos: problema · solução · execução normal · tratamento de falha · decisão técnica ·
  reflexão (limitação + uso de IA).

### Avaliação por pares (no Moodle, após a entrega final)

- Realizada individualmente no **Laboratório de Avaliação do Moodle**, com distribuição aleatória
  balanceada e **sem livre escolha** do trabalho. Em P0 cada aluno avalia **2 entregas completas de
  outros alunos, de autores distintos**.
- Pré-requisito para participar como avaliador: ter feito a própria entrega no mesmo projeto (não
  depende de nota nem aprovação).
- Cada avaliação usa escala Likert + **justificativas fundamentadas nas evidências**, indicando
  exemplos concretos e sua localização (casos de teste, resultados, trechos da documentação, momentos
  do vídeo). Comentário genérico ou marcação sem fundamentação **não atende**.
- Distinta da revisão interna dos próprios testes feita durante o desenvolvimento — ambas existem.
- **Não existe arquivo `REVISAO_PAR.md`** no repositório; nada a implementar aqui.
- Critérios, escala, pesos e composição da nota são divulgados pela coordenação antes do projeto.
