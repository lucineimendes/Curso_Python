# Documento de Design - Curso Avançado de Git

## Visão Geral

Este curso foi projetado para levar desenvolvedores do nível básico/intermediário para o nível avançado no uso do Git. O foco está no entendimento profundo dos mecanismos internos e na aplicação prática de fluxos de trabalho complexos. A estrutura é modular, permitindo que os alunos avancem em seu próprio ritmo ou consultem tópicos específicos sob demanda.

## Estrutura do Conteúdo

### Organização de Diretórios

O conteúdo do curso será organizado na seguinte estrutura de diretórios dentro do projeto:

```
/docs
  /git-course
    /01-basic
      - theory-basics.md
      - lab-first-commit.md
    /02-intermediario
      - theory-branches.md
      - lab-merge-conflict.md
    /03-avancado
      /01-internals
        - theory.md
        - lab-objects.md
      /02-advanced-history
        - theory-rebase.md
        - lab-interactive-rebase.md
      /03-workflows
        - theory-gitflow.md
        - theory-trunk-based.md
    ...
```

### Formato de Entrega

1.  **Teoria**: Arquivos Markdown com explicações detalhadas, diagramas (Mermaid) e exemplos de código.
2.  **Laboratórios Práticos**: Guias passo-a-passo para execução no terminal do aluno.
3.  **Quizzes**: Perguntas de verificação de conhecimento ao final de cada módulo (opcional para v2).
4.  **Cheat Sheet**: Um guia de referência rápida consolidado.

## Tecnologias e Ferramentas

- **Git**: Versão mais recente estável.
- **Markdown**: Para documentação.
- **Mermaid**: Para diagramas de fluxo e árvores de commit.
