"""
Módulo para avaliação de condições de desbloqueio de conquistas.

Este módulo implementa o padrão Strategy para avaliar diferentes tipos
de condições de desbloqueio, seguindo o princípio Open/Closed.
"""

import logging
from typing import Dict, Protocol

logger = logging.getLogger(__name__)


class ConditionEvaluatorStrategy(Protocol):
    """
    Protocolo para estratégias de avaliação de condições.

    Implementa o princípio Interface Segregation ao definir
    uma interface específica para avaliadores de condição.
    """

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        """
        Avalia se uma condição foi satisfeita.

        Args:
            condition (Dict): Condição de desbloqueio.
            progress_data (Dict): Dados de progresso do usuário.

        Returns:
            bool: True se a condição foi satisfeita.
        """
        ...


class LessonCountEvaluator:
    """Avalia condições baseadas em contagem de lições."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        value = condition.get("value", 0)
        return progress_data.get("total_lessons_completed", 0) >= value


class ExerciseCountEvaluator:
    """Avalia condições baseadas em contagem de exercícios."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        value = condition.get("value", 0)
        return progress_data.get("total_exercises_completed", 0) >= value


class PerfectExercisesEvaluator:
    """Avalia condições baseadas em exercícios perfeitos."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        value = condition.get("value", 0)
        achievement_stats = progress_data.get("achievement_stats", {})
        return achievement_stats.get("perfect_exercises_count", 0) >= value


class LessonsInDayEvaluator:
    """Avalia condições baseadas em lições completadas em um dia."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        value = condition.get("value", 0)
        achievement_stats = progress_data.get("achievement_stats", {})
        return achievement_stats.get("lessons_in_day", 0) >= value


class CourseCompleteEvaluator:
    """Avalia condições baseadas em conclusão de curso."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        course_id = condition.get("course_id")
        return self._is_course_complete(progress_data, course_id)

    @staticmethod
    def _is_course_complete(progress_data: Dict, course_id: str) -> bool:
        """
        Verifica se um curso específico está completo.

        Args:
            progress_data (Dict): Dados de progresso do usuário.
            course_id (str): ID do curso a verificar.

        Returns:
            bool: True se o curso está completo.
        """
        courses = progress_data.get("courses", {})
        course_progress = courses.get(course_id, {})

        # Um curso é considerado completo se tem o campo 'completed' como True
        # ou se todas as suas lições estão completas
        if course_progress.get("completed", False):
            return True

        # Verificar se todas as lições estão completas
        lessons = course_progress.get("lessons", {})
        if not lessons:
            return False

        # Todas as lições devem estar marcadas como completas
        return all(lesson.get("completed", False) for lesson in lessons.values())


class AllCoursesCompleteEvaluator:
    """Avalia condições baseadas em conclusão de todos os cursos."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        required_courses = ["python-basico", "python-intermediario", "python-avancado"]
        course_evaluator = CourseCompleteEvaluator()

        for course_id in required_courses:
            if not course_evaluator._is_course_complete(progress_data, course_id):
                return False

        return True


class ExerciseAfterAttemptsEvaluator:
    """Avalia condições baseadas em exercícios completados após N tentativas."""

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        min_attempts = condition.get("value", 0)
        courses = progress_data.get("courses", {})

        for course_progress in courses.values():
            exercises = course_progress.get("exercises", {})

            for exercise_data in exercises.values():
                # Verificar se o exercício está completo e teve pelo menos min_attempts tentativas
                if exercise_data.get("completed", False) and exercise_data.get("attempts", 0) >= min_attempts:
                    return True

        return False


class ConditionEvaluator:
    """
    Avaliador principal de condições usando o padrão Strategy.

    Implementa o princípio Open/Closed: aberto para extensão (novos avaliadores)
    mas fechado para modificação (não precisa alterar esta classe).
    """

    def __init__(self):
        """Inicializa o avaliador com todas as estratégias disponíveis."""
        self._strategies: Dict[str, ConditionEvaluatorStrategy] = {
            "lesson_count": LessonCountEvaluator(),
            "exercise_count": ExerciseCountEvaluator(),
            "perfect_exercises": PerfectExercisesEvaluator(),
            "lessons_in_day": LessonsInDayEvaluator(),
            "course_complete": CourseCompleteEvaluator(),
            "all_courses_complete": AllCoursesCompleteEvaluator(),
            "exercise_after_attempts": ExerciseAfterAttemptsEvaluator(),
        }

    def evaluate(self, condition: Dict, progress_data: Dict) -> bool:
        """
        Avalia uma condição de desbloqueio.

        Args:
            condition (Dict): Condição de desbloqueio.
            progress_data (Dict): Dados de progresso do usuário.

        Returns:
            bool: True se a condição foi satisfeita.
        """
        condition_type = condition.get("type")

        strategy = self._strategies.get(condition_type)
        if not strategy:
            logger.warning(
                f"Tipo de condição desconhecido: condition_type='{condition_type}', "
                f"available_types={list(self._strategies.keys())}"
            )
            return False

        try:
            result = strategy.evaluate(condition, progress_data)
            logger.debug(
                f"Condição avaliada: condition_type='{condition_type}', "
                f"condition_value={condition.get('value', condition.get('course_id', 'N/A'))}, "
                f"result={result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Erro ao avaliar condição: condition_type='{condition_type}', condition={condition}, error='{str(e)}'",
                exc_info=True,
            )
            return False

    def register_strategy(self, condition_type: str, strategy: ConditionEvaluatorStrategy):
        """
        Registra uma nova estratégia de avaliação.

        Permite extensão sem modificação (Open/Closed Principle).

        Args:
            condition_type (str): Tipo de condição.
            strategy (ConditionEvaluatorStrategy): Estratégia de avaliação.
        """
        self._strategies[condition_type] = strategy
        logger.info(f"Nova estratégia registrada para tipo de condição: {condition_type}")
