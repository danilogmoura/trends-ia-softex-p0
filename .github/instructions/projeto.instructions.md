---
description: "Regras do projeto (Primeiro fluxo com LLM) aplicadas a qualquer edição de código, dependências ou docs neste repositório. O nível em execução está definido em AGENTS.md."
name: "Regras de edição do projeto"
applyTo: ["**/*.py", "requirements*.txt", "README.md", ".gitignore", ".env*", "**/*.md"]
---

# Regras fixas de edição

O **nível em execução** (Básico / Intermediário / Avançado) é definido pela linha
`NÍVEL ATUAL` em `AGENTS.md`. Trabalhe só nele; não antecipe exigências de
níveis futuros. A sequência de itens, os testes previstos por commit e os gates de
cada tag estão em `PLANO.md` — verifique o próximo item pendente antes de propor
código, e feche item (`- [x]`) apenas conforme o "Protocolo de marcação" lá definido
(commit aprovado **+** evidência verificável).

## Ciclo obrigatório (não remover em nenhum nível)

Entrada textual no terminal → preparar e enviar solicitação → processar resposta → apresentar resultado.

## Nunca

- Credencial/chave/token **no código** ou commitado. Se vazar, revogar — gitignore posterior não apaga o histórico.
- Endpoint ou modelo **hardcoded**; base URL, chave e modelo vêm de configuração externa.
- `<iframe>` no README; embed de vídeo vira badge clicável.
- Inventar requisito ausente do enunciado (`docs/moodle/p0/p0-primeiro-fluxo-com-llm.md`).
- `git commit`, `git tag` ou `git push` **sem permissão explícita do usuário na conversa atual**.
  O agente prepara, testa e apresenta o diff; **quem decide o commit é o usuário, após code review**.
- Escopo proibido do P0: web, GUI, app móvel, auth de usuários, banco de dados, RAG, agentes,
  multiagente, comparação de modelos, deploy em nuvem, fine-tuning.

## Sempre

- Declarar dependências (`requirements.txt`) e a versão do Python usada.
- Commits pequenos e coerentes, PT-BR, Conventional Commits (`feat`/`fix`/`docs`) — **sempre criados pelo
  usuário ou por agente somente depois de aprovação explícita pós-review**. Ao receber o pedido, analisar
  `git diff` por completo, checar segredos no staged diff e **gerar a mensagem a partir do conteúdo real**
  (tipo conforme a natureza da mudança, escopo identificando a parte afetada).
- Terminal é interface suficiente; **um único** LLM.
- Registrar provedor/modelo escolhido quando não for o institucional.
- Ao fechar um nível, criar a tag exata: `p0-basico` · `p0-intermediario` · `p0-avancado`.
