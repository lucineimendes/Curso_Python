# Curso Interativo Python

Uma plataforma de aprendizado interativo para Python, construída com Flask.

## Sumário

*   [Funcionalidades](#funcionalidades)
*   [Tecnologias Utilizadas](#tecnologias-utilizadas)
*   [Pré-requisitos](#pré-requisitos)
*   [Instalação](#instalação)
*   [Execução](#execução)
*   [Documentação da API](#documentação-da-api)
*   [Detalhes da Arquitetura e Implementação](#detalhes-da-arquitetura-e-implementação)
    *   [Visão Geral e Estrutura Principal](#visão-geral-e-estrutura-principal)
    *   [Gerenciamento de Dados (Managers)](#gerenciamento-de-dados-managers)
    *   [Execução Segura de Código do Usuário (`code_executor.py`)](#execução-segura-de-código-do-usuário-code_executorpy)
    *   Verificação de Exercícios (`api/check-exercise`)
    *   Estratégia de Testes Automáticos
    *   Outros Aspectos
    *   Considerações sobre Escalabilidade

## Funcionalidades

*   Visualização de cursos e suas respectivas lições.
*   Conteúdo de lições apresentado de forma clara.
*   Editor de código integrado para resolução de exercícios.
*   Execução de código Python submetido pelo usuário.
*   Verificação automática de exercícios com base em testes predefinidos.
*   Navegação intuitiva entre cursos, lições e exercícios.
*   API para interações programáticas (execução de código, verificação de exercícios).

## Tecnologias Utilizadas

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript (implícito pelos templates Flask)
*   **Armazenamento de Dados:** Arquivos JSON
*   **Testes:** Pytest
*   **Outros:** `pathlib`, `logging`, `uuid`

## Pré-requisitos

*   Python 3.8 ou superior
*   uv (gerenciador de pacotes Python - recomendado) ou pip
*   Node.js e npm (para Prettier)

## Instalação

### Instalação Rápida (Recomendada)

```bash
# Executar script de setup automático
./setup.sh
```

### Instalação Manual

1.  Clone o repositório (ou baixe os arquivos do projeto).
2.  Navegue até o diretório raiz do projeto
3.  Instale o uv (se ainda não tiver):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
4.  Crie e ative um ambiente virtual:
    ```bash
    uv venv
    # Ativar ambiente virtual
    source .venv/bin/activate  # Linux/macOS
    .\.venv\Scripts\activate   # Windows
    ```
5.  Instale as dependências:
    ```bash
    uv pip install -r requirements.txt
    ```
6.  Instale dependências Node (para formatadores):
    ```bash
    npm install
    ```

## Execução

Para iniciar a aplicação em modo de desenvolvimento:

```bash
# Com uv (recomendado - não precisa ativar venv)
uv run python projects/run.py

# Ou com venv ativado
python projects/run.py

# Ou usando Make
make run
```

A aplicação estará disponível em `http://localhost:5000` (ou `http://0.0.0.0:5000`).

## Desenvolvimento

### Formatação de Código

```bash
# Formatar todo o código
make format

# Verificar formatação
make format-check

# Executar linters
make lint

# Corrigir problemas automaticamente
make lint-fix
```

### Testes

```bash
# Executar todos os testes
make test
# ou
uv run pytest

# Executar com cobertura
uv run pytest --cov=projects
```

Para mais informações sobre contribuição, veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentação

### Documentação Principal

- **[docs/INDEX.md](docs/INDEX.md)** - Índice completo da documentação técnica
- **[docs/ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md)** - Visão geral da arquitetura
- **[docs/DOCUMENTATION_STANDARDS.md](docs/DOCUMENTATION_STANDARDS.md)** - Padrões de documentação

### Documentação por Categoria

#### Arquitetura e Design
- [Sistema de Roadmap](docs/architecture/ROADMAP_SYSTEM.md) - Roadmap visual e rastreamento de progresso

#### Guias Práticos
- [Guia do UV](docs/guides/GUIDE_UV_SETUP.md) - Gerenciador de pacotes Python

#### Refatorações
- [SOLID/DRY - Sistema de Conquistas](docs/refactoring/REFACTOR_ACHIEVEMENTS_SOLID_DRY.md) - Refatoração aplicando princípios SOLID
- [Remoção de Rota Legada](docs/refactoring/LEGACY_ROUTE_REMOVAL.md) - Elimina código duplicado
- [ProgressManager](docs/refactoring/REFACTOR_PROGRESS_MANAGER.md) - Proposta de refatoração
- [Rotas da Aplicação](docs/refactoring/REFACTOR_APP_ROUTES.md) - Proposta de refatoração

#### Implementações
- [Roadmap Implementation](docs/implementation/ROADMAP_IMPLEMENTATION.md) - Sistema de roadmap visual
- [Exercise Improvements](docs/implementation/EXERCISE_IMPROVEMENTS.md) - Melhorias no sistema de exercícios
- [Summary](docs/implementation/SUMMARY.md) - Resumo de implementações
- [Final Summary](docs/implementation/FINAL_SUMMARY.md) - Resumo final completo

#### Manutenção
- [Progress Fix](docs/maintenance/PROGRESS_FIX.md) - Correção do sistema de progresso
- [Rollback Notes](docs/maintenance/ROLLBACK_NOTES.md) - Notas sobre rollback

### Documentação da API

A documentação da API está disponível através das docstrings no código-fonte. Para gerar a documentação completa:

```bash
# Gerar documentação com pydoc
uv run python -m pydoc -w projects

# Ou usar sphinx (se configurado)
make docs
```

---

## Arquitetura

O projeto segue os princípios **SOLID** e **DRY** para garantir código limpo, manutenível e extensível.

### Visão Geral

[![Estrutura do Projeto](images/Estrutura_projeto.png)](images/Estrutura_projeto.png)

- **Aplicação Flask** com separação clara entre rotas UI e API
- **Managers** para gerenciamento de dados (cursos, lições, exercícios, progresso)
- **Execução segura** de código Python com captura de stdout/stderr
- **Sistema de testes** robusto com pytest e meta-testes automáticos

### Componentes Principais

- **CourseManager**: Gerenciamento de cursos
- **LessonManager**: Gerenciamento de lições (carregamento sob demanda)
- **ExerciseManager**: Gerenciamento de exercícios (carregamento sob demanda)
- **ProgressManager**: Rastreamento de progresso do usuário
- **AchievementManager**: Sistema de conquistas (refatorado com SOLID)
- **CodeExecutor**: Execução isolada e segura de código Python

### Documentação Completa

Para detalhes completos sobre arquitetura, design patterns, refatorações e implementações, consulte:

- **[Visão Geral da Arquitetura](docs/ARCHITECTURE_OVERVIEW.md)** - Arquitetura detalhada e componentes
- **[Índice de Documentação](docs/INDEX.md)** - Índice completo de toda documentação técnica
- **[Padrões de Documentação](docs/DOCUMENTATION_STANDARDS.md)** - Convenções e padrões
