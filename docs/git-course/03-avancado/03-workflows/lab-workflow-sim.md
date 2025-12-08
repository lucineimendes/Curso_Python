# Laboratório 03: Simulação de Git Flow

**Objetivo**: Simular manualmente o ciclo de vida de uma release usando o modelo Git Flow.

## Passo 1: Setup dos Branches Principais

1.  Crie um repositório para o laboratório (se já não estiver em um).
2.  Garanta que a `master` existe (commit inicial).
3.  Crie a branch `develop`:
    ```bash
    git branch develop
    git push -u origin develop # se houver remote
    ```

## Passo 2: Iniciando uma Feature

1.  Crie uma feature a partir da `develop`:
    ```bash
    git checkout develop
    git checkout -b feature/login-page
    ```
2.  Trabalhe na feature:
    ```bash
    echo "Login Page Code" > login.html
    git add .
    git commit -m "feat: login page basics"
    ```
3.  Finalize a feature (merge na develop):
    ```bash
    git checkout develop
    git merge --no-ff feature/login-page
    ```
    *`--no-ff` cria um commit de merge explícito, preservando a história da feature.*

## Passo 3: Preparando uma Release

Imagine que temos features suficientes para a versão 1.0.

1.  Crie a release branch a partir da `develop`:
    ```bash
    git checkout -b release/1.0
    ```
2.  Faça ajustes finais (bump de versão, docs, bugfixes leves):
    ```bash
    echo "v1.0" > version.txt
    git commit -am "chore: bump version to 1.0"
    ```

## Passo 4: Finalizando a Release

1.  Merge na `master`:
    ```bash
    git checkout master
    git merge --no-ff release/1.0
    git tag -a v1.0 -m "Versão 1.0 Oficial"
    ```

2.  Merge de volta na `develop` (para que ela saiba das mudanças da release):
    ```bash
    git checkout develop
    git merge --no-ff release/1.0
    ```

3.  Apague o branch de release:
    ```bash
    git branch -d release/1.0
    ```

## Passo 5: Simulando um Hotfix

Ops! Bug crítico em produção na v1.0.

1.  Crie o hotfix a partir da `master` (a versão estável):
    ```bash
    git checkout master
    git checkout -b hotfix/conserte-login
    ```

2.  Corrija o bug:
    ```bash
    echo "Bug corrigido" >> login.html
    git commit -am "fix: correção crítica no login"
    ```

3.  Finalize o hotfix (merge em master E develop):
    ```bash
    git checkout master
    git merge --no-ff hotfix/conserte-login
    git tag v1.0.1

    git checkout develop
    git merge --no-ff hotfix/conserte-login
    ```
