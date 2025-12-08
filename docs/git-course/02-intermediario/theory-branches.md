# Módulo 02: Branches e Colaboração

## Introdução
Até agora, trabalhamos em uma linha do tempo única. Porém, em projetos reais, precisamos trabalhar em múltiplas funcionalidades simultaneamente sem interferir no trabalho dos outros. É aqui que entram os **Branches**.

## 1. O que são Branches?
Um branch é simplesmente um ponteiro móvel para um commit. O branch padrão no Git é geralmente chamado de `master` ou `main`.

### Comandos de Branching
-   `git branch`: Lista os branches existentes.
-   `git branch <nome>`: Cria um novo branch.
-   `git checkout <nome>` ou `git switch <nome>`: Muda para o branch especificado.
-   `git checkout -b <nome>`: Cria e muda para o branch em um comando.

## 2. Mesclando Alterações (Merge)
Quando terminamos o trabalho em um branch, precisamos trazer essas mudanças de volta para o branch principal.

```bash
git checkout main
git merge feature-login
```

Isso integra o histórico do branch `feature-login` no `main`.

## 3. Resolvendo Conflitos
Se duas pessoas alterarem a mesma linha do mesmo arquivo de maneiras diferentes, o Git não saberá qual escolher. Isso gera um **Conflito**.
O Git pausará o merge, marcará o arquivo conflituoso e pedirá que você resolva manualmente.

## 4. Repositórios Remotos
Para colaborar, usamos repositórios hospedados em servidores (GitHub, GitLab, Bitbucket).

-   `git clone <url>`: Copia um repositório remoto.
-   `git push origin <branch>`: Envia seus commits locais para o remoto.
-   `git pull`: Traz as atualizações do remoto para sua máquina.
