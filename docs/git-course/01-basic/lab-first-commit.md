# Laboratório 01: Seu Primeiro Commit

**Objetivo**: Configurar o Git, iniciar um repositório e fazer seu primeiro commit.

## Passo 1: Configuração

Abra seu terminal e configure sua identidade (se ainda não o fez):

```bash
git config --global user.name "Aluno Git"
git config --global user.email "aluno@curso.com"
```

## Passo 2: Inicializando o Projeto

1.  Crie uma pasta para o projeto:
    ```bash
    mkdir meu-projeto-git
    cd meu-projeto-git
    ```

2.  Inicialize o Git:
    ```bash
    git init
    ```
    *Observe que uma pasta oculta `.git` foi criada.*

## Passo 3: Criando e Salvando Arquivos

1.  Crie um arquivo chamado `hello.txt`:
    ```bash
    echo "Olá, Git!" > hello.txt
    ```

2.  Verifique o status:
    ```bash
    git status
    ```
    *O arquivo aparecerá como "Untracked".*

3.  Adicione o arquivo à Staging Area:
    ```bash
    git add hello.txt
    ```

4.  Comite o arquivo:
    ```bash
    git commit -m "Meu primeiro commit: adicionando hello.txt"
    ```

## Passo 4: Ignorando Arquivos

1.  Crie um arquivo secreto:
    ```bash
    echo "minha-senha-secreta" > segredo.txt
    ```

2.  Crie o arquivo `.gitignore` e adicione o nome do arquivo secreto:
    ```bash
    echo "segredo.txt" > .gitignore
    ```

3.  Verifique o status novamente:
    ```bash
    git status
    ```
    *Apenas o `.gitignore` deve aparecer como novo arquivo. O `segredo.txt` será ignorado.*

4.  Comite o `.gitignore`:
    ```bash
    git add .gitignore
    git commit -m "Configurando gitignore"
    ```

## Passo 5: Verificando o Histórico

Veja seus dois commits:
```bash
git log --oneline
```
