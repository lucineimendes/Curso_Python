---
description: Fluxo de desenvolvimento orientado por especificações (Spec-Driven Development) baseado no modelo Kiro
---

# 🤖 Spec-Driven Development - Guia para Agentes

Este documento é a **fonte única de verdade** para o desenvolvimento orientado por especificações neste projeto. Siga rigorosamente este fluxo ao implementar qualquer nova funcionalidade.

---

## 📌 Regra Principal

> **NUNCA inicie a implementação de uma nova funcionalidade sem antes criar e aprovar as especificações.**

---

## 📋 Estrutura de Especificações

Toda funcionalidade deve ter **três documentos obrigatórios** em `.kiro/specs/<nome-da-feature>/`:

| Arquivo | Fase | Propósito |
|---------|------|-----------|
| `requirements.md` | 1 | Histórias de usuário e critérios de aceitação (notação EARS) |
| `design.md` | 2 | Arquitetura técnica, diagramas e considerações de implementação |
| `tasks.md` | 3 | Plano de implementação com tarefas discretas e rastreáveis |

**Templates disponíveis em**: `docs/templates/`

---

## 🔄 Fluxo Obrigatório

```
INÍCIO
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│ FASE 1: REQUISITOS                                               │
│ Criar: .kiro/specs/<feature>/requirements.md                     │
│ - Definir histórias de usuário                                   │
│ - Escrever critérios de aceitação em notação EARS               │
│ - Perguntar: "O usuário aprova os requisitos?"                  │
│   ├─ NÃO → Iterar até aprovação                                 │
│   └─ SIM → Avançar para Fase 2                                  │
└──────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│ FASE 2: DESIGN                                                   │
│ Criar: .kiro/specs/<feature>/design.md                          │
│ - Documentar arquitetura técnica                                 │
│ - Criar diagramas de sequência                                   │
│ - Definir interfaces (APIs, componentes)                         │
│ - Especificar modelos de dados                                   │
│ - Planejar tratamento de erros                                   │
│ - Definir estratégia de testes                                   │
│ - Perguntar: "O usuário aprova o design?"                       │
│   ├─ NÃO → Iterar até aprovação                                 │
│   └─ SIM → Avançar para Fase 3                                  │
└──────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│ FASE 3: TAREFAS                                                  │
│ Criar: .kiro/specs/<feature>/tasks.md                           │
│ - Dividir trabalho em tarefas discretas (TASK-001, TASK-002...) │
│ - Para cada tarefa definir:                                      │
│   • Status, Descrição, Resultado esperado                        │
│   • Arquivos afetados, Dependências, Subtarefas                 │
│ - Perguntar: "O usuário aprova o plano de tarefas?"             │
│   ├─ NÃO → Iterar até aprovação                                 │
│   └─ SIM → Avançar para Fase 4                                  │
└──────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│ FASE 4: EXECUÇÃO                                                 │
│ Para cada tarefa em tasks.md (respeitando dependências):        │
│ 1. Marcar tarefa como [~] Em andamento                          │
│ 2. Implementar seguindo o design.md                              │
│ 3. Executar testes: uv run pytest                               │
│ 4. Verificar lint: uv run ruff check projects/                  │
│ 5. Marcar tarefa como [x] Concluída                             │
│ 6. Atualizar status geral no tasks.md                           │
│ 7. Repetir até todas as tarefas estarem concluídas              │
└──────────────────────────────────────────────────────────────────┘
   │
   ▼
  FIM
```

---

## 📝 Notação EARS (Obrigatória para Requisitos)

A notação **EARS** (Easy Approach to Requirements Syntax) é **obrigatória** para todos os critérios de aceitação:

```markdown
WHEN [condição ou evento que dispara a ação]
THE SYSTEM SHALL [comportamento esperado do sistema]
```

### Exemplo:

```markdown
WHEN um usuário submete um formulário com dados inválidos
THE SYSTEM SHALL exibir mensagens de erro ao lado dos campos relevantes

WHEN uma lição é completada com sucesso
THE SYSTEM SHALL verificar se alguma conquista foi desbloqueada

WHEN uma nova conquista é desbloqueada
THE SYSTEM SHALL exibir uma notificação visual celebrando o usuário
```

---

## ✅ Checklists por Fase

### Fase 1: Requisitos
- [ ] Histórias de usuário no formato "Como... Eu quero... Para..."
- [ ] Critérios de aceitação em notação EARS
- [ ] Requisitos são testáveis e mensuráveis
- [ ] Escopo claramente definido (incluindo "fora do escopo")
- [ ] **APROVAÇÃO DO USUÁRIO OBTIDA**

### Fase 2: Design
- [ ] Arquitetura documentada com diagrama
- [ ] Diagramas de sequência para fluxos principais
- [ ] APIs/Endpoints definidos com request/response
- [ ] Modelos de dados especificados
- [ ] Tratamento de erros planejado
- [ ] Estratégia de testes definida
- [ ] Princípios SOLID considerados
- [ ] Princípio DRY aplicado
- [ ] **APROVAÇÃO DO USUÁRIO OBTIDA**

### Fase 3: Tarefas
- [ ] Todas as tarefas discretas e rastreáveis (TASK-XXX)
- [ ] Cada tarefa tem resultado esperado mensurável
- [ ] Dependências entre tarefas identificadas
- [ ] Arquivos afetados listados
- [ ] Estimativas de tempo fornecidas
- [ ] **APROVAÇÃO DO USUÁRIO OBTIDA**

### Fase 4: Execução
- [ ] Cada tarefa atualizada em tempo real ([~] → [x])
- [ ] Testes executados após cada implementação
- [ ] Lint verificado antes de marcar como concluída
- [ ] Status geral atualizado no tasks.md
- [ ] Documentação atualizada (README, docs/)

---

## 🛠️ Comandos de Desenvolvimento

```bash
# Criar estrutura de nova spec
mkdir -p .kiro/specs/<nome-feature>

# Executar testes
uv run pytest

# Verificar lint
uv run ruff check projects/

# Formatar código
uv run ruff format projects/

# Rodar servidor de desenvolvimento
uv run python -m projects.app
```

---

## 📁 Estrutura de Diretórios

```
.kiro/
└── specs/
    └── <nome-da-feature>/
        ├── requirements.md    # Fase 1
        ├── design.md          # Fase 2
        └── tasks.md           # Fase 3

docs/
└── templates/
    ├── requirements.template.md
    ├── design.template.md
    └── tasks.template.md
```

---

## ⚠️ Regras Importantes

1. **Sempre peça aprovação** antes de avançar para a próxima fase
2. **Nunca pule fases** - o fluxo é sequencial e cada fase depende da anterior
3. **Mantenha documentos atualizados** - o tasks.md deve refletir o estado real
4. **Use os templates** disponíveis em `docs/templates/`
5. **Registre decisões** - documente o "porquê" das decisões de design
6. **Commits granulares** - um commit por tarefa quando possível
7. **Testes obrigatórios** - toda implementação deve ter testes

---

## 🎯 Quando Usar Este Fluxo

| Situação | Usar Spec-Driven? |
|----------|-------------------|
| Nova funcionalidade grande | ✅ SIM |
| Nova feature com múltiplos componentes | ✅ SIM |
| Refatoração significativa | ✅ SIM |
| Correção de bug simples | ❌ NÃO |
| Pequenos ajustes de UI | ❌ NÃO |
| Atualização de documentação | ❌ NÃO |

---

// turbo-all
