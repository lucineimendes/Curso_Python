# Módulo 03/04: Ferramentas Avançadas (Hooks, Bisect)

## Introdução
O Git vai muito além de add, commit e push. Ele possui ferramentas internas para automação e depuração que podem salvar horas de trabalho.

## 1. Git Hooks
Hooks são scripts executados automaticamente pelo Git antes ou depois de eventos como commit, push e receive. Eles vivem em `.git/hooks`.

### Tipos Comuns
-   **pre-commit**: Roda antes do commit ser criado. Usado para linters, formatadores e testes rápidos.
-   **commit-msg**: Valida a mensagem do commit (ex: exigir padrão "feat: ...").
-   **pre-push**: Roda antes do push. Usado para rodar a suíte completa de testes.

Para criar um hook, basta criar um arquivo executável no diretório hooks com o nome do evento.

## 2. Git Bisect: Caçando Bugs com Busca Binária
Imagine que o código funcionava na versão 1.0, mas quebrou na 2.0 (que tem 100 commits entre elas). Como achar o commit culpado?

O `git bisect` automatiza a busca binária.
1.  Você marca o commit atual como `bad`.
2.  Você marca um commit antigo como `good`.
3.  O Git faz checkout na metade do caminho.
4.  Você testa e diz se está `good` ou `bad`.
5.  O Git repete o processo até isolar o commit exato.

## 3. Git Blame
Para saber quem escreveu (e quando) cada linha de um arquivo.

```bash
git blame arquivo.py
```

Útil para entender o contexto de uma mudança, não apenas para "culpar" alguém.
