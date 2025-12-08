# Laboratório 02: Merge e Conflitos

**Objetivo**: Praticar a criação de branches, fazer merge e resolver um conflito intencional.

## Passo 1: Preparação

1.  Crie um novo diretório e inicialize o git (ou continue do lab anterior):
    ```bash
    mkdir lab-merge
    cd lab-merge
    git init
    ```

2.  Crie um arquivo base:
    ```bash
    echo "Conteúdo original" > arquivo.txt
    git add arquivo.txt
    git commit -m "Commit inicial"
    ```

## Passo 2: Criando um Feature Branch

1.  Crie e mude para um branch chamado `feature-a`:
    ```bash
    git checkout -b feature-a
    ```

2.  Modifique o arquivo:
    ```bash
    echo "Alteração da Feature A" >> arquivo.txt
    git commit -am "Feature A finalizada"
    ```

3.  Volte para a main:
    ```bash
    git checkout main
    ```
    *Observe que o conteúdo do `arquivo.txt` voltou ao original.*

## Passo 3: Criando um Conflito

1.  Crie outro branch chamado `feature-b`:
    ```bash
    git checkout -b feature-b
    ```

2.  Modifique **a mesma linha** que foi alterada na `feature-a`:
    ```bash
    echo "Alteração da Feature B (CONFLITO)" >> arquivo.txt
    git commit -am "Feature B finalizada"
    ```

## Passo 4: O Merge Conflituoso

1.  Volte para a main e faça merge da `feature-a` (sem conflito):
    ```bash
    git checkout main
    git merge feature-a
    ```

2.  Tente fazer merge da `feature-b`:
    ```bash
    git merge feature-b
    ```
    *O Git deve avisar: "CONFLICT (content): Merge conflict in arquivo.txt".*

## Passo 5: Resolvendo o Conflito

1.  Abra `arquivo.txt`. Você verá algo assim:
    ```
    Conteúdo original
    <<<<<<< HEAD
    Alteração da Feature A
    =======
    Alteração da Feature B (CONFLITO)
    >>>>>>> feature-b
    ```

2.  Edite o arquivo para deixar como você quer (ex: mantendo ambos ou escolhendo um).
    ```
    Conteúdo original
    Alteração da Feature A
    Alteração da Feature B (CONFLITO)
    ```

3.  Finalize o merge:
    ```bash
    git add arquivo.txt
    git commit -m "Merge branch feature-b: resolvendo conflitos"
    ```

Parabéns! Você resolveu seu primeiro conflito de merge.
