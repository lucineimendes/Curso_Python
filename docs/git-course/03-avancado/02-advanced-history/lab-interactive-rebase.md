# Laboratório 02: Cirurgia de Histórico

**Objetivo**: Usar `rebase -i` para limpar um histórico bagunçado e usar `reflog` para recuperar um erro intencional.

## Passo 1: Criando uma Bagunça

1.  Crie um novo repositório ou branch para o lab.
2.  Crie uma série de commits "ruins":

    ```bash
    echo "Funcionalidade A parte 1" > func.txt
    git add func.txt
    git commit -m "WIP: começando func A"

    echo "Funcionalidade A parte 2" >> func.txt
    git add func.txt
    git commit -m "continuando func A"

    echo "Erro corrigido" >> func.txt
    git add func.txt
    git commit -m "fix: corrigindo typo no commit anterior"
    ```

## Passo 2: Limpando com Squash

Queremos transformar esses 3 commits em um único commit limpo "feat: Implementar Funcionalidade A".

1.  Inicie o rebase interativo:
    ```bash
    git rebase -i HEAD~3
    ```

2.  No editor, deixe o primeiro como `pick`, e mude os outros dois para `squash` (ou `s`):
    ```
    pick [HASH1] WIP: começando func A
    squash [HASH2] continuando func A
    squash [HASH3] fix: corrigindo typo no commit anterior
    ```

3.  Salve e feche. O Git abrirá outro editor para definir a mensagem final.
4.  Apague as mensagens antigas e escreva apenas:
    ```
    feat: Implementar Funcionalidade A
    ```
5.  Salve e feche.
6.  Verifique o log: `git log --oneline`. Deve haver apenas um commit novo.

## Passo 3: Simulando um Desastre

1.  Vamos "acidentalmente" destruir nosso trabalho.
    ```bash
    git reset --hard HEAD~1
    ```
    *Agora o commit da funcionalidade sumiu do log.*

## Passo 4: Recuperando com Reflog

1.  Veja o histórico de ações:
    ```bash
    git reflog
    ```
    *Procure uma linha como `HEAD@{1}: rebase -i (finish): returning to refs/heads/...`*

2.  Recupere o commit perdido (substitua o índice):
    ```bash
    git reset --hard HEAD@{1}
    ```

3.  Verifique se o arquivo voltou:
    ```bash
    cat func.txt
    ```
