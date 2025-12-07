# Refatoração Proposta: ProgressManager

## Problema Identificado

O `ProgressManager` atual viola o princípio Single Responsibility ao ter múltiplas responsabilidades:

1. **Persistência de dados**: Carregar e salvar JSON
2. **Lógica de negócio**: Marcar lições/exercícios completos
3. **Cálculo de estatísticas**: Calcular percentuais e agregações
4. **Validação de dados**: Garantir estrutura de dados correta

## Proposta de Refatoração (SOLID/DRY)

### Estrutura Proposta

```
projects/
├── progress_manager.py          # Orquestração (refatorado)
├── progress_repository.py       # Persistência (novo - SRP)
├── progress_calculator.py       # Cálculos (novo - SRP)
└── progress_validator.py        # Validação (novo - SRP)
```

### 1. ProgressRepository (Persistência)

**Responsabilidade única**: Carregar e salvar dados de progresso

```python
class ProgressRepository:
    """Gerencia persistência de dados de progresso."""

    def __init__(self, data_dir_path_str="data"):
        self.progress_file = Path(__file__).parent / data_dir_path_str / 'user_progress.json'
        self._ensure_file_exists()

    def load(self) -> Dict:
        """Carrega dados de progresso do arquivo."""
        # Lógica de leitura JSON

    def save(self, data: Dict) -> None:
        """Salva dados de progresso no arquivo."""
        # Lógica de escrita JSON

    def _ensure_file_exists(self) -> None:
        """Garante que o arquivo existe."""
        # Lógica de criação inicial
```

### 2. ProgressCalculator (Cálculos)

**Responsabilidade única**: Calcular estatísticas e percentuais

```python
class ProgressCalculator:
    """Calcula estatísticas de progresso."""

    @staticmethod
    def calculate_course_statistics(
        course_progress: Dict,
        total_lessons: int,
        total_exercises: int
    ) -> Dict:
        """Calcula estatísticas de um curso."""
        # Lógica de cálculo

    @staticmethod
    def calculate_user_statistics(user_progress: Dict) -> Dict:
        """Calcula estatísticas gerais do usuário."""
        # Lógica de cálculo

    @staticmethod
    def calculate_completion_percentage(completed: int, total: int) -> float:
        """Calcula percentual de conclusão."""
        return (completed / total * 100) if total > 0 else 0
```

### 3. ProgressValidator (Validação)

**Responsabilidade única**: Validar estruturas de dados

```python
class ProgressValidator:
    """Valida estruturas de dados de progresso."""

    @staticmethod
    def validate_user_progress(data: Dict) -> bool:
        """Valida estrutura de progresso do usuário."""
        required_fields = ["courses", "total_lessons_completed", "total_exercises_completed"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_course_progress(data: Dict) -> bool:
        """Valida estrutura de progresso de curso."""
        required_fields = ["lessons", "exercises", "started_at"]
        return all(field in data for field in required_fields)
```

### 4. ProgressManager (Orquestração)

**Responsabilidade única**: Orquestrar operações de progresso

```python
class ProgressManager:
    """Gerencia progresso do usuário (orquestração)."""

    def __init__(self, repository=None, calculator=None, validator=None):
        # Dependency Injection
        self._repository = repository or ProgressRepository()
        self._calculator = calculator or ProgressCalculator()
        self._validator = validator or ProgressValidator()

        self.progress_data = self._repository.load()

    def mark_lesson_complete(self, user_id: str, course_id: str, lesson_id: str) -> Dict:
        """Marca lição como completa."""
        course_progress = self.get_course_progress(user_id, course_id)

        # Lógica de negócio
        if lesson_id not in course_progress["lessons"]:
            course_progress["lessons"][lesson_id] = {
                "completed": True,
                "completed_at": datetime.now().isoformat(),
                "times_viewed": 1
            }
            # Atualizar contador
            user_progress = self.get_user_progress(user_id)
            user_progress["total_lessons_completed"] += 1

        self._repository.save(self.progress_data)
        return course_progress

    def get_course_statistics(self, user_id: str, course_id: str,
                             total_lessons: int, total_exercises: int) -> Dict:
        """Obtém estatísticas do curso."""
        course_progress = self.get_course_progress(user_id, course_id)
        return self._calculator.calculate_course_statistics(
            course_progress, total_lessons, total_exercises
        )
```

## Benefícios

### Manutenibilidade
- Cada classe tem uma responsabilidade clara
- Mudanças em persistência não afetam cálculos
- Mudanças em cálculos não afetam validação

### Testabilidade
- Cada componente pode ser testado isoladamente
- Dependency Injection facilita mocks
- Testes mais rápidos e focados

### Reutilização
- `ProgressCalculator` pode ser usado em outros contextos
- `ProgressRepository` pode ser substituído (ex: migrar para BD)
- `ProgressValidator` pode validar dados de outras fontes

### Extensibilidade
- Adicionar novos cálculos: estender `ProgressCalculator`
- Adicionar novos formatos: implementar nova `Repository`
- Adicionar novas validações: estender `ProgressValidator`

## Compatibilidade

✅ **API pública mantida** (sem breaking changes)
✅ **Comportamento preservado** (mesma lógica, melhor estrutura)
✅ **Testes existentes continuam funcionando**

## Próximos Passos

1. Implementar `ProgressRepository`
2. Implementar `ProgressCalculator`
3. Implementar `ProgressValidator`
4. Refatorar `ProgressManager` para usar os novos componentes
5. Executar testes para garantir compatibilidade
6. Atualizar documentação

## Referências

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
