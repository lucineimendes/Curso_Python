"""
Módulo para validação de condições de desbloqueio de conquistas.

Este módulo implementa o princípio Single Responsibility ao separar
a lógica de validação de condições do AchievementManager.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ConditionValidator:
    """
    Valida condições de desbloqueio de conquistas.

    Responsabilidade única: validar estruturas de condições de desbloqueio.
    """

    # Tipos de condição válidos
    VALID_CONDITION_TYPES = [
        "lesson_count",
        "exercise_count",
        "perfect_exercises",
        "lessons_in_day",
        "course_complete",
        "all_courses_complete",
        "exercise_after_attempts",
    ]

    # Tipos que requerem 'value'
    CONDITIONS_REQUIRING_VALUE = [
        "lesson_count",
        "exercise_count",
        "perfect_exercises",
        "lessons_in_day",
        "exercise_after_attempts",
    ]

    @classmethod
    def validate_condition(cls, condition: Dict, achievement_id: str = "unknown") -> bool:
        """
        Valida se uma condição de desbloqueio está bem formada.

        Args:
            condition (Dict): Condição a ser validada.
            achievement_id (str): ID da conquista (para logging).

        Returns:
            bool: True se a condição é válida, False caso contrário.
        """
        if not isinstance(condition, dict):
            logger.warning(
                f"Erro de validação: achievement_id='{achievement_id}', "
                f"error='unlock_condition não é um dicionário', condition_type={type(condition).__name__}"
            )
            return False

        if "type" not in condition:
            logger.warning(
                f"Erro de validação: achievement_id='{achievement_id}', "
                f"error='unlock_condition está faltando campo type', condition={condition}"
            )
            return False

        condition_type = condition.get("type")
        if condition_type not in cls.VALID_CONDITION_TYPES:
            logger.warning(
                f"Erro de validação: achievement_id='{achievement_id}', "
                f"error='tipo de condição desconhecido', condition_type='{condition_type}', "
                f"valid_types={cls.VALID_CONDITION_TYPES}"
            )
            return False

        # Validar que condições que precisam de 'value' o tenham
        if condition_type in cls.CONDITIONS_REQUIRING_VALUE:
            if "value" not in condition:
                logger.warning(
                    f"Erro de validação: achievement_id='{achievement_id}', "
                    f"error='condição requer campo value', condition_type='{condition_type}'"
                )
                return False

            # Validar que value é um número
            if not isinstance(condition.get("value"), (int, float)):
                logger.warning(
                    f"Erro de validação: achievement_id='{achievement_id}', "
                    f"error='campo value deve ser um número', condition_type='{condition_type}', "
                    f"value_type={type(condition.get('value')).__name__}, value={condition.get('value')}"
                )
                return False

        # Validar que course_complete tem course_id
        if condition_type == "course_complete":
            if "course_id" not in condition:
                logger.warning(
                    f"Erro de validação: achievement_id='{achievement_id}', "
                    f"error='condição course_complete requer campo course_id', condition={condition}"
                )
                return False

        logger.debug(f"Validação bem-sucedida: achievement_id='{achievement_id}', condition_type='{condition_type}'")
        return True


class AchievementValidator:
    """
    Valida definições completas de conquistas.

    Responsabilidade única: validar estruturas de conquistas.
    """

    REQUIRED_FIELDS = ["id", "name", "description", "icon", "unlock_condition"]

    @classmethod
    def validate_achievement(cls, achievement: Dict) -> bool:
        """
        Valida se uma definição de conquista contém todos os campos obrigatórios.

        Args:
            achievement (Dict): Definição de conquista a ser validada.

        Returns:
            bool: True se a conquista é válida, False caso contrário.
        """
        if not isinstance(achievement, dict):
            logger.warning(
                f"Erro de validação: error='conquista não é um dicionário', "
                f"achievement_type={type(achievement).__name__}"
            )
            return False

        achievement_id = achievement.get("id", "desconhecido")

        # Verificar campos obrigatórios
        missing_fields = []
        empty_fields = []

        for field in cls.REQUIRED_FIELDS:
            if field not in achievement:
                missing_fields.append(field)
            elif not achievement[field]:
                empty_fields.append(field)

        if missing_fields:
            logger.warning(
                f"Erro de validação: achievement_id='{achievement_id}', "
                f"error='campos obrigatórios faltando', missing_fields={missing_fields}"
            )
            return False

        if empty_fields:
            logger.warning(
                f"Erro de validação: achievement_id='{achievement_id}', "
                f"error='campos obrigatórios vazios', empty_fields={empty_fields}"
            )
            return False

        # Validar estrutura de unlock_condition
        unlock_condition = achievement.get("unlock_condition")
        is_valid = ConditionValidator.validate_condition(unlock_condition, achievement_id)

        if is_valid:
            logger.debug(f"Validação bem-sucedida: achievement_id='{achievement_id}', name='{achievement.get('name')}'")

        return is_valid
