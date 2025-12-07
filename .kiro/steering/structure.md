# Estrutura do Projeto

## Organização de Diretórios

```
projects/                    # Pacote principal da aplicação
├── app.py                  # Aplicação Flask principal, rotas UI e API
├── run.py                  # Script de inicialização do servidor
├── course_manager.py       # Gerenciamento de dados de cursos
├── lesson_manager.py       # Gerenciamento de dados de lições
├── exercise_manager.py     # Gerenciamento de dados de exercícios
├── progress_manager.py     # Gerenciamento de progresso do usuário
├── achievement_manager.py  # Gerenciamento de conquistas (refatorado SOLID)
├── condition_validator.py  # Validação de condições de conquistas (SRP)
├── condition_evaluator.py  # Avaliação de condições (Strategy Pattern, OCP)
├── code_executor.py        # Execução segura de código Python
├── data/                   # Armazenamento de dados JSON
│   ├── achievements.json   # Definições de conquistas
│   ├── courses.json        # Lista de cursos disponíveis
│   ├── user_progress.json  # Progresso dos usuários
│   ├── basic/              # Dados do curso básico
│   ├── intermediate/       # Dados do curso intermediário
│   └── advanced/           # Dados do curso avançado
├── static/                 # Assets estáticos
│   ├── css/
│   │   ├── style.css       # Estilos principais + tema escuro
│   │   └── roadmap.css     # Estilos do roadmap
│   └── js/
│       ├── main.js         # JavaScript principal + alternância de tema
│       ├── editor.js       # Integração CodeMirror
│       ├── roadmap.js      # Componente do roadmap visual
│       └── exercise_handler.js  # Gerenciamento de exercícios
├── templates/              # Templates Jinja2
└── testes/                 # Suite de testes
    ├── conftest.py         # Fixtures pytest e configuração
    ├── test_app.py         # Testes de rotas e API
    └── test_meta_exercise.py  # Meta-testes para validação de exercícios
```

## Padrões Arquiteturais

### Separação UI/API
- **Rotas UI**: Renderizam templates HTML (`/`, `/courses`, `/courses/<id>`, `/courses/<id>/roadmap`)
- **Rotas API**: Retornam JSON, prefixadas com `/api` (`/api/execute-code`, `/api/check-exercise`, `/api/progress/*`)

### Managers (Camada de Dados)
- **CourseManager**: Carrega todos os cursos na inicialização
- **LessonManager**: Carrega lições sob demanda via `load_lessons_from_file()`
- **ExerciseManager**: Carrega exercícios sob demanda via `load_exercises_from_file()`
- **ProgressManager**: Gerencia progresso do usuário (lições/exercícios completados, estatísticas)
- **AchievementManager**: Gerencia conquistas (refatorado com SOLID/DRY)
  - Usa Dependency Injection para validators e evaluators
  - Delega validação para `AchievementValidator`
  - Delega avaliação para `ConditionEvaluator` (Strategy Pattern)
- Otimização: Managers de lições/exercícios não carregam todos os dados na inicialização

### Execução de Código
- `code_executor.execute_code()`: Executa código do usuário, captura stdout/stderr
- `code_executor.execute_test()`: Executa código de teste com namespace customizado
- Variável `output` disponibilizada para `test_code` contendo stdout do código do usuário

### Sistema de Progresso
- **ProgressManager**: Gerencia progresso do usuário através dos cursos
- **Persistência**: Dados salvos em `data/user_progress.json`
- **API RESTful**: Endpoints para marcar lições/exercícios como completos
- **Frontend**: Roadmap visual interativo com estatísticas em tempo real
- **Sincronização**: localStorage (frontend) + JSON (backend)

## Convenções de Código

### Imports
- Imports relativos dentro do pacote `projects`: `from .course_manager import CourseManager`
- `pathlib.Path` para manipulação de caminhos de arquivo
- Logging configurado em nível de módulo: `logger = logging.getLogger(__name__)`

### Nomenclatura
- Funções de rota UI: sufixo `_page` (ex: `course_detail_page`)
- Funções de rota API: prefixo `api_` (ex: `api_execute_code`)
- Managers: sufixo `_mgr` para instâncias (ex: `course_mgr`)

### Tratamento de Erros
- Uso de `abort()` do Flask para erros HTTP
- Handlers customizados para 404 e 500
- Logging extensivo com níveis apropriados (DEBUG, INFO, WARNING, ERROR)

### Dados JSON
- IDs sempre comparados como strings: `str(course.get('id')) == str(course_id)`
- Validação de tipo: `isinstance(data, dict)` antes de processar
- Encoding UTF-8 explícito: `encoding='utf-8'` em operações de arquivo

## Estratégia de Testes

### Fixtures (conftest.py)
- `app`: Instância Flask configurada para testes
- `client`: Cliente de teste Flask
- `app_test_data` (autouse): Cria dados temporários e faz monkeypatch dos managers

### Isolamento
- `tmp_path` do pytest para diretórios temporários
- `monkeypatch` para substituir `DATA_DIR` e `data_dir` dos managers
- Cada teste executa com dados isolados, sem afetar arquivos reais

### Meta-testes
- `test_meta_exercise.py` varre todos os arquivos de exercícios
- Valida que `solution_code` passa no `test_code` correspondente
- Garante qualidade do conteúdo de forma automatizada

## Pontos de Atenção

- Rota legada `/submit_exercise` mantida para compatibilidade (considerar refatoração)
- `courses_file` vs `couses.json` (typo no nome do arquivo - verificar se é usado)
- Escalabilidade: JSON funciona para escala atual, considerar BD para crescimento futuro
- Sistema de progresso usa `user_id="default"` - implementar autenticação para multi-usuário
- Progresso salvo em localStorage pode ser perdido - sincronizar com backend regularmente
