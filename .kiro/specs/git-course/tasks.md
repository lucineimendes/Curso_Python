# Plano de Implementação - Curso Avançado de Git

- [x] 0.1 Criar conteúdo para Módulo Básico
  - Escrever `docs/git-course/01-basic/theory-basics.md`
  - Escrever `docs/git-course/01-basic/lab-first-commit.md`
  - _Requisito: Básico_

- [x] 0.2 Criar conteúdo para Módulo Intermediário
  - Escrever `docs/git-course/02-intermediario/theory-branches.md`
  - Escrever `docs/git-course/02-intermediario/lab-merge-conflict.md`
  - _Requisito: Intermediário_

- [x] 1. Criar conteúdo para Módulo 1: Internals
  - Escrever `docs/git-course/03-avancado/01-internals/theory.md`
  - Escrever `docs/git-course/03-avancado/01-internals/lab-objects.md`
  - _Requisito: 1_

- [x] 2. Criar conteúdo para Módulo 2: Histórico Avançado
  - Escrever `docs/git-course/03-avancado/02-advanced-history/theory-rebase.md`
  - Escrever `docs/git-course/03-avancado/02-advanced-history/lab-interactive-rebase.md`
  - _Requisito: 2_

- [x] 3. Criar conteúdo para Módulo 3: Workflows
  - Escrever `docs/git-course/03-avancado/03-workflows/theory-gitflow.md`
  - Escrever `docs/git-course/03-avancado/03-workflows/lab-workflow-sim.md`
  - _Requisito: 3_

- [x] 4. Criar conteúdo para Módulo 4: Ferramentas
  - Escrever `docs/git-course/03-avancado/04-tools/theory-hooks.md`
  - Escrever `docs/git-course/03-avancado/04-tools/lab-bisect.md`
  - _Requisito: 4_

- [x] 5. Criar conteúdo para Módulo 5: Estruturas Complexas
  - Escrever `docs/git-course/03-avancado/05-complex-structures/theory-submodules.md`
  - Escrever `docs/git-course/03-avancado/05-complex-structures/theory-lfs.md`
  - _Requisito: 5_

- [x] 6. Criar Referência Rápida
  - Escrever `docs/git-course/cheat-sheet.md`
  - _Requisito: 6_

- [x] 7. Criar script de conversão e gerar arquivos JSON
  - Criar `convert_git_course.py` para converter Markdown para JSON
  - Gerar `projects/data/git-advanced/lessons.json` com todas as lições
  - Gerar `projects/data/git-advanced/exercises.json` (estrutura inicial)
  - _Requisito: Todos_

- [x] 8. Criar exercícios interativos para o curso
  - [x] 8.1 Criar exercícios para Módulo Básico
    - Adicionar exercícios práticos de `git init`, `git add`, `git commit`
    - Adicionar exercício de configuração do `.gitignore`
    - _Requisito: Básico.1, Básico.2, Básico.3, Básico.4_

  - [x] 8.2 Criar exercícios para Módulo Intermediário
    - Adicionar exercícios de criação e troca de branches
    - Adicionar exercício de merge básico
    - Adicionar exercício de resolução de conflitos
    - _Requisito: Intermediário.1, Intermediário.2, Intermediário.3_

  - [x] 8.3 Criar exercícios para Módulo Internals
    - Adicionar exercício de exploração do diretório `.git`
    - Adicionar exercício usando `git hash-object` e `git cat-file`
    - _Requisito: 1.1, 1.2, 1.3, 1.4_

  - [x] 8.4 Criar exercícios para Módulo Histórico Avançado
    - Adicionar exercício de `git commit --amend`
    - Adicionar exercício de `git rebase -i` (squash, reword)
    - Adicionar exercício de `git reflog` para recuperação
    - _Requisito: 2.1, 2.2, 2.4_

  - [x] 8.5 Criar exercícios para Módulo Workflows
    - Adicionar exercício simulando Git Flow (feature branch)
    - Adicionar exercício simulando GitHub Flow
    - _Requisito: 3.1, 3.2, 3.3_

  - [x] 8.6 Criar exercícios para Módulo Ferramentas
    - Adicionar exercício de criação de Git Hook (pre-commit)
    - Adicionar exercício simulado de `git bisect`
    - _Requisito: 4.1, 4.2_
