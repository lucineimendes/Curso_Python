# Módulo 03/03: Workflows e Estratégias

## Introdução
Não basta saber os comandos; é preciso saber como trabalhar em equipe. Git Workflows são "contratos" de como a equipe usará branches e merges para entregar software.

## 1. Git Flow (O Clássico)
Popularizado por Vincent Driessen, é ideal para projetos com ciclos de release bem definidos (versões 1.0, 1.1, etc).

**Estrutura de Branches:**
-   `master`: Histórico de produção. Apenas releases oficiais.
-   `develop`: Branch de integração principal.
-   `feature/*`: Novas funcionalidades. Nascem e morrem na `develop`.
-   `release/*`: Preparação para nova versão (apenas bugfixes). Merge na `master` e `develop`.
-   `hotfix/*`: Correção urgente em produção. Nasce da `master`, merge em `master` e `develop`.

## 2. Trunk-Based Development (O Moderno)
Focado em integração contínua (CI/CD) e velocidade.

**Princípios:**
-   Branch principal (`trunk` ou `main`) está sempre "deployável".
-   Branches de feature (se existirem) duram no máximo 1-2 dias.
-   Muitas vezes comita-se direto na `main` (se houver testes robustos).
-   Se a feature não está pronta, usa-se **Feature Flags** para escondê-la, em vez de isolar o código em branch.

## 3. GitHub Flow
Uma simplificação do Git Flow, muito usada em web apps.

1.  Branch `main` é deployável.
2.  Crie um branch descritivo (`new-oauth`) a partir da `main`.
3.  Faça commits.
4.  Abra um **Pull Request** para discussão e review.
5.  Merge na `main` e deploy imediato.

## 4. Feature Flags
Desacoplar **Deploy** (instalação de código) de **Release** (liberação para usuário).
O código entra em produção desligado (`if flag_enabled: new_feature()`) e é ligado gradualmente. Isso elimina a necessidade de branches de longa duração.
