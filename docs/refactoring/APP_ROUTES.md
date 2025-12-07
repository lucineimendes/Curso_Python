# Refatoração Proposta: app.py

## Problemas Identificados

### 1. Violação do DRY (Don't Repeat Yourself)

**Código Duplicado**: A rota legada `/submit_exercise` duplica toda a lógica de `/api/check-exercise`

```python
# Linhas 750-850: Lógica duplicada
@app.route('/submit_exercise/<string:course_id>/<string:exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    # ... 100+ linhas de código duplicado ...
```

**Impacto**:
- Manutenção duplicada (bugs precisam ser corrigidos em dois lugares)
- Inconsistências entre as duas rotas
- Código mais difícil de testar

### 2. Violação do SRP (Single Responsibility Principle)

**app.py tem múltiplas responsabilidades**:
- Roteamento HTTP
- Validação de dados
- Lógica de negócio (buscar cursos, exercícios, validar níveis)
- Orquestração de managers
- Tratamento de erros

**Impacto**:
- Arquivo muito grande (879 linhas)
- Difícil de testar (lógica misturada com rotas)
- Difícil de reutilizar lógica em outros contextos

### 3. Lógica de Negócio nas Rotas

Exemplo: Validação de nível de exercício repetida em múltiplas rotas

```python
# Repetido em lesson_detail_page, exercise_code_editor_page, api_check_exercise
course_level_from_course_json = current_course.get('level')
expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

# ... depois ...
if not expected_exercise_level or ex_item.get('level', '').lower() == expected_exercise_level:
    # ...
```

## Proposta de Refatoração

### Estrutura Proposta

```
projects/
├── app.py                      # Apenas rotas (refatorado)
├── services/                   # Camada de serviços (novo)
│   ├── __init__.py
│   ├── course_service.py       # Lógica de negócio de cursos
│   ├── exercise_service.py     # Lógica de negócio de exercícios
│   └── progress_service.py     # Lógica de negócio de progresso
└── validators/                 # Validadores (novo)
    ├── __init__.py
    └── request_validator.py    # Validação de requisições
```

### 1. ExerciseService (Lógica de Negócio)

**Responsabilidade única**: Lógica de negócio relacionada a exercícios

```python
# projects/services/exercise_service.py

class ExerciseService:
    """Serviço para lógica de negócio de exercícios."""

    def __init__(self, course_mgr, exercise_mgr, code_executor):
        self.course_mgr = course_mgr
        self.exercise_mgr = exercise_mgr
        self.code_executor = code_executor

    def get_exercise_for_course(self, course_id: str, exercise_id: str) -> Optional[Dict]:
        """
        Obtém um exercício validando seu nível com o curso.

        Centraliza a lógica repetida de validação de nível.
        """
        course = self.course_mgr.get_course_by_id(course_id)
        if not course:
            return None

        exercises_file = course.get("exercises_file")
        if not exercises_file:
            raise ValueError(f"Arquivo de exercícios não definido para curso '{course_id}'")

        expected_level = course.get('level', '').lower()
        exercises = self.exercise_mgr.load_exercises_from_file(exercises_file)

        for exercise in exercises:
            if str(exercise.get('id')) == str(exercise_id):
                exercise_level = exercise.get('level', '').lower()
                if not expected_level or exercise_level == expected_level:
                    return exercise

        return None

    def check_exercise_solution(self, course_id: str, exercise_id: str,
                                user_code: str) -> Dict:
        """
        Verifica solução de exercício.

        Centraliza a lógica de verificação (DRY).
        """
        exercise = self.get_exercise_for_course(course_id, exercise_id)
        if not exercise:
            raise ValueError(f"Exercício '{exercise_id}' não encontrado")

        # 1. Executar código do usuário
        user_result = self.code_executor.execute_code(user_code)
        user_stdout = user_result["stdout"]
        user_success = user_result["returncode"] == 0

        if not user_success:
            return {
                "success": False,
                "output": user_stdout,
                "details": user_result["stderr"] or "Erro na execução"
            }

        # 2. Executar test_code se existir
        test_code = exercise.get("test_code", "")
        if not test_code:
            return {
                "success": True,
                "output": user_stdout,
                "details": "Código executado (sem testes automáticos)"
            }

        test_globals = {'output': user_stdout}
        test_result = self.code_executor.execute_code(test_code, execution_globals=test_globals)
        test_success = test_result["returncode"] == 0

        combined_output = user_stdout + test_result["stdout"]
        details = test_result["stderr"] if not test_success else "Teste passou"

        return {
            "success": test_success,
            "output": combined_output,
            "details": details
        }
```

### 2. RequestValidator (Validação)

**Responsabilidade única**: Validar requisições HTTP

```python
# projects/validators/request_validator.py

class RequestValidator:
    """Valida requisições HTTP."""

    @staticmethod
    def validate_execute_code_request(data: Dict) -> tuple[bool, Optional[str]]:
        """
        Valida requisição de execução de código.

        Returns:
            (is_valid, error_message)
        """
        if not data or 'code' not in data:
            return False, "Payload inválido ou campo 'code' ausente"
        return True, None

    @staticmethod
    def validate_check_exercise_request(data: Dict) -> tuple[bool, Optional[str]]:
        """
        Valida requisição de verificação de exercício.

        Returns:
            (is_valid, error_message)
        """
        required_fields = ['course_id', 'exercise_id', 'code']
        if not data or not all(k in data for k in required_fields):
            return False, f"Campos obrigatórios: {', '.join(required_fields)}"
        return True, None

    @staticmethod
    def validate_progress_request(data: Dict, required_fields: List[str]) -> tuple[bool, Optional[str]]:
        """
        Valida requisição de progresso.

        Returns:
            (is_valid, error_message)
        """
        if not data or not all(k in data for k in required_fields):
            return False, f"Campos obrigatórios: {', '.join(required_fields)}"
        return True, None
```

### 3. app.py Refatorado (Apenas Rotas)

```python
# projects/app.py (refatorado)

from .services.exercise_service import ExerciseService
from .validators.request_validator import RequestValidator

# Inicializar serviços
exercise_service = ExerciseService(course_mgr, exercise_mgr, code_executor)
request_validator = RequestValidator()

@app.route('/api/check-exercise', methods=['POST'])
def api_check_exercise():
    """API endpoint para verificar solução de exercício."""
    logger.info("POST /api/check-exercise")

    data = request.get_json()

    # Validação
    is_valid, error_msg = request_validator.validate_check_exercise_request(data)
    if not is_valid:
        return jsonify({"success": False, "details": error_msg}), 400

    # Lógica de negócio (delegada ao serviço)
    try:
        result = exercise_service.check_exercise_solution(
            data['course_id'],
            data['exercise_id'],
            data['code']
        )

        # Registrar progresso
        user_id = data.get('user_id', 'default')
        progress_mgr.mark_exercise_attempt(
            user_id,
            data['course_id'],
            data['exercise_id'],
            result['success']
        )

        return jsonify(result)

    except ValueError as e:
        return jsonify({"success": False, "details": str(e)}), 404
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({"success": False, "details": f"Erro interno: {str(e)}"}), 500

@app.route('/submit_exercise/<string:course_id>/<string:exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    """Rota legada - redireciona para nova API."""
    logger.warning("Rota legada /submit_exercise chamada")

    # Extrair código
    data = request.get_json() or {}
    user_code = data.get('code') or request.form.get('code')

    if not user_code:
        return jsonify({"success": False, "details": "Campo 'code' obrigatório"}), 400

    # Reutilizar lógica da nova API (DRY)
    try:
        result = exercise_service.check_exercise_solution(
            course_id, exercise_id_str, user_code
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"success": False, "details": str(e)}), 404
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({"success": False, "details": f"Erro interno: {str(e)}"}), 500
```

## Benefícios

### Eliminação de Duplicação (DRY)
- ✅ Lógica de verificação centralizada em `ExerciseService`
- ✅ Rota legada reutiliza nova implementação
- ✅ Validação de nível centralizada

### Separação de Responsabilidades (SRP)
- ✅ `app.py`: Apenas roteamento HTTP
- ✅ `ExerciseService`: Lógica de negócio
- ✅ `RequestValidator`: Validação de dados
- ✅ Managers: Acesso a dados

### Testabilidade
- ✅ Serviços podem ser testados sem Flask
- ✅ Validadores podem ser testados isoladamente
- ✅ Rotas ficam mais simples de testar

### Manutenibilidade
- ✅ Bugs corrigidos em um único lugar
- ✅ Código mais fácil de entender
- ✅ Mudanças isoladas

## Métricas de Melhoria

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Linhas em app.py | 879 | ~500 | -43% |
| Código duplicado | ~100 linhas | 0 | -100% |
| Responsabilidades de app.py | 5 | 1 | -80% |
| Testabilidade | Baixa | Alta | +100% |

## Plano de Implementação

1. ✅ Criar `docs/refactoring/APP_ROUTES.md`
2. ⬜ Criar `projects/services/__init__.py`
3. ⬜ Implementar `ExerciseService`
4. ⬜ Implementar `RequestValidator`
5. ⬜ Refatorar rotas em `app.py`
6. ⬜ Executar testes
7. ⬜ Remover código duplicado
8. ⬜ Atualizar documentação

## Compatibilidade

✅ **API pública mantida** (mesmas rotas e respostas)
✅ **Comportamento preservado** (mesma lógica, melhor estrutura)
✅ **Rota legada continua funcionando** (agora sem duplicação)
