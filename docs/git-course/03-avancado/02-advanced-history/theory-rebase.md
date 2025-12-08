# Módulo 03/02: Manipulação Avançada de Histórico

## Introdução
Um histórico limpo conta uma história clara sobre a evolução do projeto. O Git oferece ferramentas poderosas para reescrever essa história, mas é preciso usá-las com cuidado ("Com grandes poderes...").

## 1. Reescrevendo com Rebase Interativo

O `git rebase -i` (interativo) permite editar uma série de commits. Você pode:
-   **reword**: Alterar a mensagem do commit.
-   **edit**: Parar para alterar o conteúdo do commit.
-   **squash/fixup**: Fundir o commit no anterior.
-   **drop**: Remover o commit.

```bash
git rebase -i HEAD~3
```
*Isso abre um editor com os últimos 3 commits para você manipular.*

## 2. Emendando o Último Commit

Se você esqueceu de adicionar um arquivo ou errou na mensagem do último commit (e ainda não fez push):

```bash
git commit --amend
```
Isso substitui o último commit por um novo.

## 3. Cherry-Picking

Às vezes você precisa aplicar apenas um commit específico de outro branch no seu.

```bash
git cherry-pick [HASH_DO_COMMIT]
```

## 4. O Reflog: Sua Rede de Segurança

Quando você faz rebase ou reset, parece que você "perdeu" commits. Na verdade, o Git mantém um registro de onde HEAD esteve nos últimos dias.

```bash
git reflog
```
Você pode recuperar qualquer estado anterior:
```bash
git reset --hard HEAD@{12}
```

## 5. Limpando Histórico (BFG / Filter-Repo)

Se você acidentalmente comitou senhas ou arquivos gigantes, ferramentas como `git-filter-repo` (o sucessor do `filter-branch`) são necessárias para reescrever todo o histórico e remover esses objetos.

> **Aviso**: Reescrever histórico de branches públicos quebra o repositório para outros colaboradores. Só faça isso em branches locais ou se tiver coordenado com a equipe.
