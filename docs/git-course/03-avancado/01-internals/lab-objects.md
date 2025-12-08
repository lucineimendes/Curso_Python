# Laboratório 01: Explorando Objetos do Git

**Objetivo**: Manipular diretamente o banco de dados do Git (encanamento/plumbing) para entender como Blobs, Trees e Commits são formados.

## Passo 1: O Banco de Dados de Objetos

1.  Crie um repositório limpo:
    ```bash
    mkdir lab-internals
    cd lab-internals
    git init
    ```

2.  Explore a pasta objects:
    ```bash
    find .git/objects -type f
    ```
    *Deve estar vazia (exceto pack/info).*

## Passo 2: Criando um Blob Manualmente

O comando `git hash-object` calcula o hash e opcionalmente grava o objeto.

1.  Grave uma string no banco de dados:
    ```bash
    echo "conteúdo secreto" | git hash-object -w --stdin
    ```
    *O comando retornará um hash, ex: `d670460...`*

2.  Verifique a pasta objects novamente:
    ```bash
    find .git/objects -type f
    ```
    *Você verá um arquivo criado com os 2 primeiros caracteres do hash como pasta e o restante como nome.*

## Passo 3: Lendo o Conteúdo

O comando `git cat-file` investiga objetos.

1.  Verifique o tipo do objeto (use os primeiros 6 chars do hash retornado acima):
    ```bash
    git cat-file -t [HASH]
    ```
    *Deve retornar `blob`.*

2.  Leia o conteúdo:
    ```bash
    git cat-file -p [HASH]
    ```
    *Deve retornar "conteúdo secreto".*

## Passo 4: Explorando Commits Existentes

Vamos ver como um commit real se parece.

1.  Faça um commit normal:
    ```bash
    echo "Olá" > arquivo.txt
    git add arquivo.txt
    git commit -m "Commit de teste"
    ```

2.  Descubra o hash do commit atual (HEAD):
    ```bash
    git rev-parse HEAD
    ```

3.  Inspecione o commit:
    ```bash
    git cat-file -p [HASH_DO_COMMIT]
    ```
    *Observe que ele aponta para uma `tree` e contém autor/committer.*

4.  Inspecione a Tree apontada pelo commit:
    ```bash
    git cat-file -p [HASH_DA_TREE]
    ```
    *Observe que ela mapeia `arquivo.txt` para um hash de `blob`.*

5.  Inspecione o Blob final:
    ```bash
    git cat-file -p [HASH_DO_BLOB]
    ```
    *Deve ser "Olá".*
