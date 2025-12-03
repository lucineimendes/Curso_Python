# Sistema de Roadmap e Progresso

## Visão Geral

O sistema de roadmap fornece uma visualização interativa do progresso do usuário através dos cursos, lições e exercícios. Inclui:

- **Roadmap Visual**: Mapa interativo com checkpoints e ramificações
- **Rastreamento de Progresso**: Acompanhamento automático de lições e exercícios completados
- **Estatísticas**: Métricas detalhadas de progresso
- **Persistência**: Dados salvos em JSON e localStorage

## Arquitetura

### Backend (Python)

#### ProgressManager (`projects/progress_manager.py`)

Gerencia todo o progresso do usuário:

```python
from projects.progress_manager import ProgressManager

progress_mgr = ProgressManager()

# Marcar lição como completa
progress_mgr.mark_lesson_complete(user_id, course_id, lesson_id)

# Marcar exercício como completo
progress_mgr.mark_exercise_complete(user_id, course_id, exercise_id, success=True)

# Obter estatísticas
stats = progress_mgr.get_course_statistics(user_id, course_id, total_lessons, total_exercises)
```

**Estrutura de Dados:**

```json
{
  "users": {
    "default": {
      "courses": {
        "python-basico": {
          "lessons": {
            "introducao-python": {
              "completed": true,
              "completed_at": "2024-01-15T10:30:00",
              "times_viewed": 3
            }
          },
          "exercises": {
            "ex-introducao-1": {
              "completed": true,
              "completed_at": "2024-01-15T11:00:00",
              "attempts": 2,
              "first_attempt_success": false
            }
          },
          "started_at": "2024-01-15T10:00:00",
          "last_accessed": "2024-01-15T11:00:00"
        }
      },
      "total_lessons_completed": 5,
      "total_exercises_completed": 12
    }
  }
}
```

### Frontend (JavaScript)

#### CourseRoadmap (`projects/static/js/roadmap.js`)

Classe JavaScript para gerenciar o roadmap visual:

```javascript
const roadmap = new CourseRoadmap(courseId, 'course-roadmap');
roadmap.render(lessons, exercises);

// Marcar como completo
roadmap.markLessonComplete(lessonId);
roadmap.markExerciseComplete(exerciseId);
```

**Funcionalidades:**

- Renderização do mapa visual
- Cálculo de estatísticas em tempo real
- Sincronização com servidor
- Persistência em localStorage
- Animações e interações

### Estilos (CSS)

#### roadmap.css (`projects/static/css/roadmap.css`)

Estilos completos para o roadmap:

- Nós do roadmap (checkpoints)
- Conectores entre nós
- Barras de progresso
- Animações de transição
- Suporte a tema escuro
- Responsividade

## API Endpoints

### POST /api/progress/lesson

Marca uma lição como completa.

**Request:**
```json
{
  "course_id": "python-basico",
  "lesson_id": "introducao-python",
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lição marcada como completa",
  "progress": { ... }
}
```

### POST /api/progress/exercise

Marca um exercício como completo.

**Request:**
```json
{
  "course_id": "python-basico",
  "exercise_id": "ex-introducao-1",
  "success": true,
  "attempts": 1,
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Exercício atualizado",
  "progress": { ... }
}
```

### GET /api/progress/course/<course_id>

Obtém progresso completo de um curso.

**Query Parameters:**
- `user_id` (opcional): ID do usuário (padrão: "default")

**Response:**
```json
{
  "success": true,
  "course": { ... },
  "progress": { ... },
  "statistics": {
    "completed_lessons": 3,
    "total_lessons": 10,
    "lessons_percentage": 30,
    "completed_exercises": 5,
    "total_exercises": 15,
    "exercises_percentage": 33.33,
    "overall_percentage": 31.67
  },
  "lessons": [ ... ],
  "exercises": [ ... ]
}
```

### GET /api/progress/user

Obtém estatísticas gerais do usuário.

**Query Parameters:**
- `user_id` (opcional): ID do usuário (padrão: "default")

**Response:**
```json
{
  "success": true,
  "statistics": {
    "user_id": "default",
    "total_courses_started": 3,
    "total_courses_completed": 1,
    "total_lessons_completed": 15,
    "total_exercises_completed": 30
  }
}
```

## Rotas HTML

### GET /courses/<course_id>/roadmap

Renderiza a página de roadmap visual do curso.

**Template:** `course_roadmap.html`

**Dados Passados:**
- `course`: Dados do curso
- `lessons`: Lista de lições
- `exercises`: Lista de exercícios

## Uso

### Visualizar Roadmap

1. Acesse a página de detalhes do curso
2. Clique no botão "🗺️ Ver Roadmap do Curso"
3. Visualize seu progresso no mapa interativo

### Marcar Progresso Automaticamente

O progresso é marcado automaticamente quando:

- **Lições**: Ao acessar uma lição (pode ser implementado)
- **Exercícios**: Ao completar um exercício com sucesso

### Marcar Progresso Manualmente

Via JavaScript:

```javascript
// Marcar lição
if (window.courseRoadmap) {
    window.courseRoadmap.markLessonComplete(lessonId);
}

// Marcar exercício
if (window.courseRoadmap) {
    window.courseRoadmap.markExerciseComplete(exerciseId);
}
```

Via API:

```javascript
fetch('/api/progress/lesson', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        course_id: 'python-basico',
        lesson_id: 'introducao-python'
    })
});
```

## Personalização

### Adicionar Novos Checkpoints

Edite `roadmap.js` para adicionar novos tipos de checkpoints:

```javascript
renderLessonsMap(lessons, exercises) {
    // Adicionar lógica para novos tipos de nós
}
```

### Customizar Estilos

Edite `roadmap.css` para personalizar:

```css
.roadmap-node.custom-type {
    /* Estilos personalizados */
}
```

### Adicionar Métricas

Edite `progress_manager.py` para adicionar novas métricas:

```python
def get_custom_statistics(self, user_id, course_id):
    # Calcular métricas personalizadas
    pass
```

## Integração com Outros Sistemas

### Sistema de Gamificação

```python
# Adicionar pontos ao completar lição
def mark_lesson_complete(self, user_id, course_id, lesson_id):
    # ... código existente ...
    self._award_points(user_id, 'lesson_complete', 10)
```

### Sistema de Certificados

```python
# Verificar se curso está completo para emitir certificado
stats = progress_mgr.get_course_statistics(user_id, course_id, total_lessons, total_exercises)
if stats['is_complete']:
    certificate_mgr.issue_certificate(user_id, course_id)
```

### Notificações

```python
# Enviar notificação ao completar marco
if completed_lessons % 5 == 0:
    notification_mgr.send(user_id, f"Parabéns! Você completou {completed_lessons} lições!")
```

## Testes

### Testar Backend

```python
# test_progress_manager.py
def test_mark_lesson_complete():
    progress_mgr = ProgressManager()
    result = progress_mgr.mark_lesson_complete('test_user', 'test_course', 'test_lesson')
    assert result['lessons']['test_lesson']['completed'] == True
```

### Testar Frontend

```javascript
// Testar renderização do roadmap
const roadmap = new CourseRoadmap('test-course', 'test-container');
roadmap.render(mockLessons, mockExercises);
assert(document.querySelectorAll('.roadmap-node').length === mockLessons.length);
```

### Testar API

```bash
# Testar endpoint de progresso
curl -X POST http://localhost:5000/api/progress/lesson \
  -H "Content-Type: application/json" \
  -d '{"course_id":"python-basico","lesson_id":"introducao-python"}'
```

## Troubleshooting

### Progresso não está sendo salvo

1. Verificar permissões do arquivo `user_progress.json`
2. Verificar logs do servidor para erros
3. Verificar localStorage do navegador

### Roadmap não está renderizando

1. Verificar se `courseData` está definido no template
2. Verificar console do navegador para erros JavaScript
3. Verificar se CSS está carregado corretamente

### Estatísticas incorretas

1. Verificar se total de lições/exercícios está correto
2. Limpar cache do progresso: `localStorage.clear()`
3. Recarregar dados do servidor

## Melhorias Futuras

- [ ] Sistema de conquistas/badges
- [ ] Comparação de progresso com outros usuários
- [ ] Exportar progresso em PDF
- [ ] Gráficos de progresso ao longo do tempo
- [ ] Recomendações personalizadas baseadas em progresso
- [ ] Modo offline com sincronização posterior
- [ ] Integração com calendário para metas
- [ ] Notificações push de progresso
