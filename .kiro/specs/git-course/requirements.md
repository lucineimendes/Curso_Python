# Requisitos do Curso Avançado de Git

### Requisito Básico: Primeiros Passos com Git

**História de Usuário:** Como um estudante iniciante, eu quero aprender a versionar meu código localmente, para que eu possa salvar meu progresso e experimentar sem medo de perder meu trabalho.

#### Critérios de Aceitação

1. O módulo deve ensinar a instalação e configuração inicial (user.name, user.email).
2. O módulo deve explicar o ciclo básico: `git init`, `git add`, `git commit`.
3. O módulo deve demonstrar como visualizar o histórico com `git log`.
4. O módulo deve ensinar como ignorar arquivos indesejados com `.gitignore`.

### Requisito Intermediário: Colaboração e Branches Básicos

**História de Usuário:** Como um desenvolvedor júnior, eu quero aprender a trabalhar com branches, para que eu possa desenvolver novas funcionalidades sem quebrar o código principal do projeto.

#### Critérios de Aceitação

1. O módulo deve ensinar a criar e trocar de branches (`git branch`, `git checkout`/`git switch`).
2. O módulo deve explicar como mesclar alterações com `git merge`.
3. O módulo deve demonstrar como resolver conflitos de merge básicos.
4. O módulo deve introduzir o conceito de repositórios remotos (`git remote`, `git push`, `git pull`).


### Requisito 1: Fundamentos Internos do Git (Internals)

**História de Usuário:** Como um desenvolvedor experiente, eu quero entender como o Git armazena dados internamente, para que eu possa depurar problemas complexos e entender o porquê de certos comportamentos.

#### Critérios de Aceitação

1. O módulo deve explicar a estrutura do diretório `.git` (HEAD, config, refs, objects).
2. O módulo deve detalhar os objetos do Git: Blobs, Trees, Commits e Tags.
3. O módulo deve demonstrar como o Git usa SHA-1 para endereçamento de conteúdo.
4. O módulo deve incluir um laboratório prático manipulando `git hash-object` e `git cat-file`.

### Requisito 2: Manipulação Avançada de Histórico

**História de Usuário:** Como um mantenedor de projetos, eu quero aprender a reescrever o histórico de commits de forma segura, para manter a árvore do projeto limpa e compreensível.

#### Critérios de Aceitação

1. O módulo deve cobrir `git rebase -i` com todas as suas opções (squash, fixup, edit, etc.).
2. O módulo deve ensinar como editar o último commit com `git commit --amend`.
3. O módulo deve explicar como usar `git cherry-pick` e seus riscos.
4. O módulo deve demonstrar o uso do `git reflog` para recuperação de desastres.
5. O módulo deve apresentar ferramentas de limpeza como `git filter-repo` (ou filter-branch/BFG).

### Requisito 3: Estratégias de Branching e Workflows

**História de Usuário:** Como um líder técnico, eu quero conhecer diferentes fluxos de trabalho, para escolher e implementar o mais adequado para minha equipe.

#### Critérios de Aceitação

1. O módulo deve detalhar o Git Flow clássico.
2. O módulo deve detalhar o Trunk-Based Development.
3. O módulo deve detalhar o GitHub Flow.
4. O módulo deve explicar o conceito e uso de Feature Flags.
5. O módulo deve incluir um laboratório simulando um ciclo de release.

### Requisito 4: Ferramentas e Automação

**História de Usuário:** Como um engenheiro de DevOps, eu quero automatizar tarefas repetitivas e garantir qualidade no código, para aumentar a produtividade da equipe.

#### Critérios de Aceitação

1. O módulo deve ensinar a configurar Git Hooks (client-side e server-side).
2. O módulo deve demonstrar o uso do `git bisect` para debug.
3. O módulo deve explicar o uso de `git worktrees`.
4. O módulo deve mostrar como criar e usar Git Aliases.

### Requisito 5: Submodules, Monorepos e Arquivos Grandes

**História de Usuário:** Como um arquiteto de software, eu quero saber gerenciar repositórios grandes e dependências complexas, para escalar o desenvolvimento sem perder performance.

#### Critérios de Aceitação

1. O módulo deve comparar Git Submodules e Git Subtree.
2. O módulo deve ensinar a configurar e usar Git LFS.
3. O módulo deve apresentar estratégias para Monorepos (sparse-checkout, partial clone).

### Requisito 6: Referência Rápida (Cheat Sheet)

**História de Usuário:** Como um aluno do curso, eu quero ter um guia de consulta rápida, para lembrar dos comandos essenciais durante o trabalho diário.

#### Critérios de Aceitação

1. O guia deve listar comandos essenciais do dia-a-dia (status, log, diff).
2. O guia deve listar comandos de gerenciamento de branches.
3. O guia deve listar comandos de sincronização remota.
4. O guia deve listar comandos de desfazer mudanças e Stash.