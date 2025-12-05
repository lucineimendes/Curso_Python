"""
Módulo para gerenciamento de conquistas e badges.

Este módulo gerencia o sistema de conquistas, incluindo carregamento de definições,
validação, verificação de condições de desbloqueio e persistência de conquistas desbloqueadas.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class AchievementManager:
    """
    Gerencia conquistas e badges do sistema.

    Responsabilidades:
    - Carregar definições de conquistas do JSON
    - Verificar condições de desbloqueio
    - Persistir conquistas desbloqueadas
    - Fornecer dados de conquistas para a API
    """

    def __init__(self, data_dir_path_str="data"):
        """
        Inicializa o AchievementManager.

        Args:
            data_dir_path_str (str): Caminho para o diretório de dados.
        """
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / data_dir_path_str
        self.achievements_file = self.data_dir / "achievements.json"

        self.achievements = self.load_achievements()
        logger.info(
            f"AchievementManager inicializado. {len(self.achievements)} conquistas carregadas de: {self.achievements_file}"
        )

    def load_achievements(self) -> List[Dict]:
        """
        Carrega definições de conquistas do arquivo JSON.

        Returns:
            List[Dict]: Lista de definições de conquistas válidas.
        """
        if not self.achievements_file.exists():
            logger.warning(f"Arquivo de conquistas '{self.achievements_file}' não encontrado. Retornando lista vazia.")
            return []

        try:
            with open(self.achievements_file, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "achievements" not in data:
                logger.error(
                    f"Formato inválido em {self.achievements_file}. Esperava objeto com chave 'achievements'. Retornando lista vazia."
                )
                return []

            achievements_list = data.get("achievements", [])
            if not isinstance(achievements_list, list):
                logger.error("Formato inválido: 'achievements' não é uma lista. Retornando lista vazia.")
                return []

            # Validar e filtrar conquistas
            valid_achievements = []
            for achievement in achievements_list:
                if self._validate_achievement(achievement):
                    valid_achievements.append(achievement)
                else:
                    logger.warning(f"Conquista inválida ignorada: {achievement.get('id', 'ID desconhecido')}")

            logger.info(f"{len(valid_achievements)} conquistas válidas carregadas de {len(achievements_list)} total.")
            return valid_achievements

        except json.JSONDecodeError:
            logger.error(
                f"Erro ao decodificar JSON de '{self.achievements_file}'. Retornando lista vazia.",
                exc_info=True,
            )
            return []
        except OSError as e:
            logger.error(
                f"Erro de I/O ao ler '{self.achievements_file}': {e}. Retornando lista vazia.",
                exc_info=True,
            )
            return []

    def get_all_achievements(self) -> List[Dict]:
        """
        Retorna todas as definições de conquistas disponíveis.

        Returns:
            List[Dict]: Lista de todas as conquistas carregadas.
        """
        return self.achievements

    def _validate_achievement(self, achievement: Dict) -> bool:
        """
        Valida se uma definição de conquista contém todos os campos obrigatórios.

        Args:
            achievement (Dict): Definição de conquista a ser validada.

        Returns:
            bool: True se a conquista é válida, False caso contrário.
        """
        if not isinstance(achievement, dict):
            logger.warning("Conquista não é um dicionário")
            return False

        # Campos obrigatórios
        required_fields = ["id", "name", "description", "icon", "unlock_condition"]

        for field in required_fields:
            if field not in achievement:
                logger.warning(
                    f"Conquista '{achievement.get('id', 'desconhecido')}' está faltando campo obrigatório: {field}"
                )
                return False

            # Verificar que campos não estão vazios
            if not achievement[field]:
                logger.warning(f"Conquista '{achievement.get('id', 'desconhecido')}' tem campo vazio: {field}")
                return False

        # Validar estrutura de unlock_condition
        unlock_condition = achievement.get("unlock_condition")
        if not isinstance(unlock_condition, dict):
            logger.warning(f"Conquista '{achievement.get('id')}': unlock_condition não é um dicionário")
            return False

        if "type" not in unlock_condition:
            logger.warning(f"Conquista '{achievement.get('id')}': unlock_condition está faltando campo 'type'")
            return False

        # Validar tipos de condição conhecidos
        valid_condition_types = [
            "lesson_count",
            "exercise_count",
            "perfect_exercises",
            "lessons_in_day",
            "course_complete",
            "all_courses_complete",
            "exercise_after_attempts",
        ]

        condition_type = unlock_condition.get("type")
        if condition_type not in valid_condition_types:
            logger.warning(f"Conquista '{achievement.get('id')}': tipo de condição desconhecido '{condition_type}'")
            return False

        # Validar que condições que precisam de 'value' o tenham
        conditions_requiring_value = [
            "lesson_count",
            "exercise_count",
            "perfect_exercises",
            "lessons_in_day",
            "exercise_after_attempts",
        ]

        if condition_type in conditions_requiring_value:
            if "value" not in unlock_condition:
                logger.warning(f"Conquista '{achievement.get('id')}': condição '{condition_type}' requer campo 'value'")
                return False

            # Validar que value é um número
            if not isinstance(unlock_condition.get("value"), (int, float)):
                logger.warning(f"Conquista '{achievement.get('id')}': campo 'value' deve ser um número")
                return False

        # Validar que course_complete tem course_id
        if condition_type == "course_complete":
            if "course_id" not in unlock_condition:
                logger.warning(
                    f"Conquista '{achievement.get('id')}': condição 'course_complete' requer campo 'course_id'"
                )
                return False

        return True
